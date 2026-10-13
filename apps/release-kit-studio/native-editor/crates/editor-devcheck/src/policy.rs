use crate::model::Violation;
use serde_json::Value;
use std::collections::{BTreeMap, BTreeSet};
use std::fs;
use std::path::{Path, PathBuf};
use syn::spanned::Spanned;
use syn::visit::Visit;

const BANNED: &[&str] = &[
    "ffmpeg",
    "libav",
    "python",
    "node",
    "bun",
    "tauri",
    "effect",
    "cloudflare",
    "pyo3",
    "mlua",
    "rlua",
    "deno",
    "napi",
];
fn banned(name: &str) -> bool {
    let name = name.to_lowercase();
    BANNED.iter().any(|word| name.contains(word))
}
fn ident_text(ident: &syn::Ident) -> String {
    ident.to_string().trim_start_matches("r#").to_string()
}
fn path_text(path: &syn::Path) -> String {
    format!(
        "{}{}",
        if path.leading_colon.is_some() {
            "::"
        } else {
            ""
        },
        path.segments
            .iter()
            .map(|s| ident_text(&s.ident))
            .collect::<Vec<_>>()
            .join("::")
    )
}
fn imports(tree: &syn::UseTree, prefix: String, result: &mut BTreeMap<String, String>) {
    match tree {
        syn::UseTree::Path(p) => imports(
            &p.tree,
            format!("{prefix}{}::", ident_text(&p.ident)),
            result,
        ),
        syn::UseTree::Name(n) => {
            result.insert(
                ident_text(&n.ident),
                format!("{prefix}{}", ident_text(&n.ident)),
            );
        }
        syn::UseTree::Rename(n) => {
            result.insert(
                ident_text(&n.rename),
                format!("{prefix}{}", ident_text(&n.ident)),
            );
        }
        syn::UseTree::Group(g) => {
            for t in &g.items {
                imports(t, prefix.clone(), result)
            }
        }
        syn::UseTree::Glob(_) => {
            result.insert(format!("{prefix}*"), prefix);
        }
    }
}
struct SourceVisitor<'a> {
    role: &'a str,
    file: &'a Path,
    aliases: BTreeMap<String, String>,
    attribute_base: PathBuf,
    module_base: PathBuf,
    violations: Vec<Violation>,
    external: Vec<PathBuf>,
}
impl SourceVisitor<'_> {
    fn violation(&mut self, code: &str, message: impl Into<String>, span: proc_macro2::Span) {
        let mut v = Violation::new(code, Some(self.file.display().to_string()), message);
        v.line = Some(span.start().line);
        self.violations.push(v);
    }
    fn resolve(&self, path: &str) -> String {
        if path.starts_with("::") {
            return path.trim_start_matches("::").to_string();
        }
        let mut resolved = path.to_string();
        for _ in 0..self.aliases.len() + 1 {
            let first = resolved.split("::").next().unwrap_or_default();
            let Some(prefix) = self.aliases.get(first) else {
                break;
            };
            let next = format!("{}{}", prefix, &resolved[first.len()..]);
            if next == resolved {
                break;
            }
            resolved = next;
        }
        resolved
    }
    fn process_path(&mut self, path: &str, span: proc_macro2::Span) {
        let normalized = path.trim_start_matches("::");
        let syntactic_process = normalized.starts_with("std::process")
            || normalized.starts_with("std::os::unix::process")
            || normalized.starts_with("std::os::windows::process");
        let resolved = if syntactic_process {
            normalized.to_string()
        } else {
            self.resolve(path)
        };
        if self.aliases.iter().any(|(alias, value)| {
            alias.ends_with("::*")
                && [
                    "std::",
                    "::std::",
                    "std::process::",
                    "std::os::unix::process::",
                    "std::os::windows::process::",
                ]
                .contains(&self.resolve(value).as_str())
        }) {
            self.violation(
                "runtime-process",
                "Standard-library wildcard import obscures process ownership",
                span,
            );
            return;
        }
        if resolved.starts_with("std::process")
            || resolved.starts_with("std::os::unix::process")
            || resolved.starts_with("std::os::windows::process")
        {
            if self.role == "editor-cli"
                && ["std::process::exit", "::std::process::exit"].contains(&path)
            {
                return;
            }
            self.violation(
                "runtime-process",
                format!("{} cannot use {resolved}", self.role),
                span,
            );
        }
    }
}
impl<'ast> Visit<'ast> for SourceVisitor<'_> {
    fn visit_item_use(&mut self, node: &'ast syn::ItemUse) {
        let mut values = BTreeMap::new();
        imports(&node.tree, String::new(), &mut values);
        for value in values.values() {
            self.process_path(value, node.span());
        }
        syn::visit::visit_item_use(self, node);
    }
    fn visit_path(&mut self, node: &'ast syn::Path) {
        self.process_path(&path_text(node), node.span());
        syn::visit::visit_path(self, node);
    }
    fn visit_item_impl(&mut self, node: &'ast syn::ItemImpl) {
        if node.unsafety.is_some() {
            self.violation("runtime-unsafe", "Unsafe impl is forbidden", node.span());
        }
        syn::visit::visit_item_impl(self, node);
    }
    fn visit_item_trait(&mut self, node: &'ast syn::ItemTrait) {
        if node.unsafety.is_some() {
            self.violation("runtime-unsafe", "Unsafe trait is forbidden", node.span());
        }
        syn::visit::visit_item_trait(self, node);
    }
    fn visit_expr_unsafe(&mut self, node: &'ast syn::ExprUnsafe) {
        self.violation(
            "runtime-unsafe",
            "Runtime unsafe code is forbidden",
            node.span(),
        );
        syn::visit::visit_expr_unsafe(self, node);
    }
    fn visit_item_fn(&mut self, node: &'ast syn::ItemFn) {
        if node.sig.unsafety.is_some() {
            self.violation(
                "runtime-unsafe",
                "Unsafe function is forbidden",
                node.span(),
            );
        }
        syn::visit::visit_item_fn(self, node);
    }
    fn visit_item_mod(&mut self, node: &'ast syn::ItemMod) {
        fn external(meta: &syn::Meta, base: &Path, paths: &mut Vec<PathBuf>) {
            if let syn::Meta::NameValue(value) = meta {
                if value.path.is_ident("path") {
                    if let syn::Expr::Lit(expr) = &value.value {
                        if let syn::Lit::Str(path) = &expr.lit {
                            paths.push(base.join(path.value()));
                        }
                    }
                }
            }
            if let syn::Meta::List(list) = meta {
                if list.path.is_ident("cfg_attr") {
                    use syn::parse::Parser;
                    if let Ok(items) =
                        syn::punctuated::Punctuated::<syn::Meta, syn::Token![,]>::parse_terminated
                            .parse2(list.tokens.clone())
                    {
                        for item in items {
                            external(&item, base, paths)
                        }
                    }
                }
            }
        }
        let mut selected = vec![];
        for attr in &node.attrs {
            external(&attr.meta, &self.attribute_base, &mut selected);
        }
        self.external.extend(selected.clone());
        if node.content.is_none() && selected.is_empty() {
            let name = ident_text(&node.ident);
            let file = self.module_base.join(format!("{name}.rs"));
            let nested = self.module_base.join(name).join("mod.rs");
            if file.exists() {
                self.external.push(file)
            } else if nested.exists() {
                self.external.push(nested)
            }
        }
        let old_attribute = self.attribute_base.clone();
        let old_module = self.module_base.clone();
        if node.content.is_some() {
            self.attribute_base = self.attribute_base.join(ident_text(&node.ident));
            self.module_base = self.module_base.join(ident_text(&node.ident));
        }
        syn::visit::visit_item_mod(self, node);
        self.attribute_base = old_attribute;
        self.module_base = old_module;
    }
    fn visit_macro(&mut self, node: &'ast syn::Macro) {
        let name = path_text(&node.path);
        if name == "include" {
            self.violation(
                "runtime-include",
                "Generated or external include source is forbidden",
                node.span(),
            );
            if let Ok(path) = syn::parse2::<syn::LitStr>(node.tokens.clone()) {
                self.external
                    .push(self.file.parent().unwrap().join(path.value()));
            }
        }
        let tokens = node.tokens.to_string().replace(' ', "");
        if tokens.contains("std::process::") || tokens.contains("Command::new(") {
            self.violation(
                "runtime-process-macro",
                "Process tokens inside a runtime macro require removal",
                node.span(),
            );
        }
        syn::visit::visit_macro(self, node);
    }
    fn visit_lit_str(&mut self, node: &'ast syn::LitStr) {
        let text = node.value().to_lowercase();
        if [
            "ffmpeg",
            "libav",
            "editor-local.mjs",
            "editor/engine",
            "python",
        ]
        .iter()
        .any(|w| text.contains(w))
        {
            self.violation(
                "renderer-literal",
                "Forbidden renderer literal",
                node.span(),
            );
        }
        syn::visit::visit_lit_str(self, node);
    }
}
struct AliasVisitor {
    aliases: BTreeMap<String, String>,
}
impl<'ast> Visit<'ast> for AliasVisitor {
    fn visit_item_extern_crate(&mut self, node: &'ast syn::ItemExternCrate) {
        if let Some((_, alias)) = &node.rename {
            self.aliases
                .insert(ident_text(alias), ident_text(&node.ident));
        }
        syn::visit::visit_item_extern_crate(self, node);
    }
    fn visit_item_use(&mut self, node: &'ast syn::ItemUse) {
        imports(&node.tree, String::new(), &mut self.aliases);
        syn::visit::visit_item_use(self, node);
    }
}
pub fn analyze_source(role: &str, path: &Path, source: &str) -> (Vec<Violation>, Vec<PathBuf>) {
    match syn::parse_file(source) {
        Err(error) => (
            vec![Violation::new(
                "rust-parse",
                Some(path.display().to_string()),
                error.to_string(),
            )],
            vec![],
        ),
        Ok(ast) => {
            let mut aliases = AliasVisitor {
                aliases: BTreeMap::new(),
            };
            aliases.visit_file(&ast);
            let mut visitor = SourceVisitor {
                role,
                file: path,
                aliases: aliases.aliases,
                attribute_base: path.parent().unwrap_or_else(|| Path::new(".")).to_owned(),
                module_base: {
                    let parent = path.parent().unwrap_or_else(|| Path::new("."));
                    let stem = path.file_stem().unwrap_or_default().to_string_lossy();
                    if ["lib", "main", "mod"].contains(&stem.as_ref()) {
                        parent.to_owned()
                    } else {
                        parent.join(stem.as_ref())
                    }
                },
                violations: vec![],
                external: vec![],
            };
            visitor.visit_file(&ast);
            (visitor.violations, visitor.external)
        }
    }
}
fn rust_files(path: &Path, out: &mut Vec<PathBuf>, violations: &mut Vec<Violation>) {
    match fs::symlink_metadata(path) {
        Ok(meta) if meta.file_type().is_symlink() => violations.push(Violation::new(
            "source-symlink",
            Some(path.display().to_string()),
            "Symlink source is forbidden",
        )),
        Ok(meta) if meta.is_dir() => match fs::read_dir(path) {
            Ok(entries) => {
                for e in entries {
                    match e {
                        Ok(e) => rust_files(&e.path(), out, violations),
                        Err(e) => {
                            violations.push(Violation::new("source-read", None, e.to_string()))
                        }
                    }
                }
            }
            Err(e) => violations.push(Violation::new("source-read", None, e.to_string())),
        },
        Ok(_) if path.extension().is_some_and(|e| e == "rs") => out.push(path.to_owned()),
        Ok(_) => {}
        Err(e) => violations.push(Violation::new(
            "source-read",
            Some(path.display().to_string()),
            e.to_string(),
        )),
    }
}
pub fn runtime_sources(root: &Path) -> Vec<Violation> {
    let mut violations = vec![];
    for role in ["editor-core", "editor-cli"] {
        let base = root.join("crates").join(role);
        let mut files = vec![];
        rust_files(&base.join("src"), &mut files, &mut violations);
        if let Ok(text) = fs::read_to_string(base.join("Cargo.toml")) {
            if let Ok(manifest) = text.parse::<toml::Value>() {
                if let Some(build) = manifest
                    .get("package")
                    .and_then(|p| p.get("build"))
                    .and_then(|p| p.as_str())
                {
                    files.push(base.join(build));
                }
                if base.join("build.rs").exists() {
                    files.push(base.join("build.rs"));
                }
                for target in ["lib", "bin"] {
                    if let Some(value) = manifest.get(target) {
                        let targets = value
                            .as_array()
                            .cloned()
                            .unwrap_or_else(|| vec![value.clone()]);
                        for t in targets {
                            if let Some(p) = t.get("path").and_then(|p| p.as_str()) {
                                files.push(base.join(p));
                            }
                        }
                    }
                }
            }
        }
        let mut visited = BTreeSet::new();
        while let Some(path) = files.pop() {
            let canonical = match fs::canonicalize(&path) {
                Ok(p) => p,
                Err(e) => {
                    violations.push(Violation::new(
                        "source-read",
                        Some(path.display().to_string()),
                        e.to_string(),
                    ));
                    continue;
                }
            };
            if !visited.insert(canonical) {
                continue;
            }
            if fs::symlink_metadata(&path).is_ok_and(|m| m.file_type().is_symlink()) {
                violations.push(Violation::new(
                    "source-symlink",
                    Some(path.display().to_string()),
                    "Symlink source is forbidden",
                ));
                continue;
            }
            match fs::read_to_string(&path) {
                Ok(source) => {
                    let (v, external) = analyze_source(role, &path, &source);
                    violations.extend(v);
                    files.extend(external)
                }
                Err(e) => violations.push(Violation::new(
                    "source-read",
                    Some(path.display().to_string()),
                    e.to_string(),
                )),
            }
        }
    }
    let base = root.join("crates/editor-devcheck/src");
    let mut files = vec![];
    rust_files(&base, &mut files, &mut violations);
    let mut visited = BTreeSet::new();
    while let Some(path) = files.pop() {
        if !visited.insert(path.clone()) {
            continue;
        }
        if path == base.join("process.rs") {
            continue;
        }
        match fs::read_to_string(&path) {
            Ok(source) => {
                let (found, external) =
                    analyze_source("development-non-process-owner", &path, &source);
                violations.extend(found.into_iter().filter(|v| {
                    v.code == "runtime-process"
                        || v.code == "runtime-process-macro"
                        || v.code == "runtime-include"
                        || v.code == "rust-parse"
                }));
                files.extend(external);
            }
            Err(e) => violations.push(Violation::new(
                "source-read",
                Some(path.display().to_string()),
                e.to_string(),
            )),
        }
    }
    if let Ok(source) = fs::read_to_string(base.join("process.rs")) {
        if source.contains("wait_with_output") || source.contains(".output(") {
            violations.push(Violation::new(
                "unbounded-process",
                None,
                "ProcessRunner cannot use unbounded output shortcuts",
            ));
        }
    }
    violations
}
pub fn analyze_manifest(role: &str, path: &Path, text: &str) -> Vec<Violation> {
    let mut v = vec![];
    let value = match text.parse::<toml::Value>() {
        Ok(v) => v,
        Err(e) => {
            return vec![Violation::new(
                "manifest-parse",
                Some(path.display().to_string()),
                e.to_string(),
            )]
        }
    };
    let runtime = role != "editor-devcheck";
    if value
        .get("package")
        .and_then(|p| p.get("name"))
        .and_then(|p| p.as_str())
        != Some(role)
    {
        v.push(Violation::new(
            "crate-role",
            Some(path.display().to_string()),
            "Package name differs from compiled role",
        ));
    }
    if runtime
        && (value.get("build-dependencies").is_some()
            || value
                .get("package")
                .and_then(|p| p.get("build"))
                .is_some_and(|b| b.as_bool() != Some(false))
            || path.parent().unwrap().join("build.rs").exists())
    {
        v.push(Violation::new(
            "runtime-build",
            Some(path.display().to_string()),
            "Runtime build scripts and build dependencies are forbidden",
        ));
    }
    fn tables<'a>(table: &'a toml::Value, out: &mut Vec<(&'a str, &'a toml::Value)>) {
        if let Some(t) = table.as_table() {
            for (k, v) in t {
                if matches!(
                    k.as_str(),
                    "dependencies" | "build-dependencies" | "dev-dependencies"
                ) {
                    out.push((k, v));
                } else {
                    tables(v, out)
                }
            }
        }
    }
    let mut dependencies = vec![];
    tables(&value, &mut dependencies);
    for (kind, table) in dependencies {
        if runtime && kind == "build-dependencies" {
            v.push(Violation::new(
                "runtime-build",
                Some(path.display().to_string()),
                "Target build dependencies are forbidden",
            ));
        }
        if let Some(entries) = table.as_table() {
            for (alias, dep) in entries {
                let package = dep.get("package").and_then(|p| p.as_str()).unwrap_or(alias);
                let allowed = match role {
                    "editor-core" => [
                        "serde",
                        "serde_json",
                        "schemars",
                        "serde_jcs",
                        "sha2",
                        "rusqlite",
                        "png",
                    ]
                    .contains(&package),
                    "editor-cli" => ["editor-core", "serde", "serde_json", "schemars", "sha2"]
                        .contains(&package),
                    _ => package != "editor-core" && package != "editor-cli",
                };
                if (kind != "dev-dependencies" && !allowed)
                    || (role == "editor-devcheck"
                        && ["editor-core", "editor-cli"].contains(&package))
                    || package.contains("ffmpeg")
                    || package.contains("libav")
                    || (runtime && kind != "dev-dependencies" && banned(package))
                {
                    v.push(Violation::new(
                        "dependency-role",
                        Some(path.display().to_string()),
                        format!("{role} dependency {alias} resolves to disallowed {package}"),
                    ));
                }
            }
        }
    }
    v
}
pub fn ownership(root: &Path) -> Vec<Violation> {
    let mut v = vec![];
    let text = match fs::read_to_string(root.join("Cargo.toml")) {
        Ok(t) => t,
        Err(e) => return vec![Violation::new("manifest-read", None, e.to_string())],
    };
    let workspace = match text.parse::<toml::Value>() {
        Ok(v) => v,
        Err(e) => return vec![Violation::new("manifest-parse", None, e.to_string())],
    };
    let expected: BTreeSet<_> = [
        "crates/editor-core",
        "crates/editor-cli",
        "crates/editor-devcheck",
    ]
    .into_iter()
    .collect();
    if workspace.get("package").is_some() {
        v.push(Violation::new(
            "workspace-root-package",
            Some(root.join("Cargo.toml").display().to_string()),
            "Root package has no compiled workspace role",
        ));
    }
    let actual: BTreeSet<_> = workspace
        .get("workspace")
        .and_then(|w| w.get("members"))
        .and_then(|m| m.as_array())
        .map(|a| a.iter().filter_map(|v| v.as_str()).collect())
        .unwrap_or_default();
    if expected != actual {
        v.push(Violation::new(
            "workspace-roles",
            None,
            "Workspace members differ from compiled roles",
        ));
    }
    for role in ["editor-core", "editor-cli", "editor-devcheck"] {
        let path = root.join("crates").join(role).join("Cargo.toml");
        match fs::read_to_string(&path) {
            Ok(text) => v.extend(analyze_manifest(role, &path, &text)),
            Err(e) => v.push(Violation::new(
                "manifest-read",
                Some(path.display().to_string()),
                e.to_string(),
            )),
        }
    }
    v
}
pub fn dependencies(metadata: &Value) -> Vec<Violation> {
    let mut v = vec![];
    let Some(packages) = metadata["packages"].as_array() else {
        return vec![Violation::new("metadata-shape", None, "Missing packages")];
    };
    let names: BTreeMap<_, _> = packages
        .iter()
        .filter_map(|p| Some((p["id"].as_str()?, p["name"].as_str()?)))
        .collect();
    let resolved_roles: BTreeSet<_> = metadata["workspace_members"]
        .as_array()
        .map(|ids| {
            ids.iter()
                .filter_map(|id| id.as_str().and_then(|id| names.get(id)).copied())
                .collect()
        })
        .unwrap_or_default();
    let expected_roles: BTreeSet<_> = ["editor-core", "editor-cli", "editor-devcheck"]
        .into_iter()
        .collect();
    if resolved_roles != expected_roles {
        v.push(Violation::new(
            "resolved-workspace-roles",
            None,
            "Resolved workspace members differ from the three compiled crate roles",
        ));
    }
    let Some(nodes) = metadata["resolve"]["nodes"].as_array() else {
        return vec![Violation::new(
            "metadata-shape",
            None,
            "Missing resolved nodes",
        )];
    };
    for name in names.values() {
        if name.contains("ffmpeg") || name.contains("libav") {
            v.push(Violation::new(
                "resolved-backend",
                None,
                format!("Banned workspace backend {name}"),
            ));
        }
    }
    for node in nodes {
        let Some(role) = node["id"].as_str().and_then(|id| names.get(id)).copied() else {
            continue;
        };
        if !["editor-core", "editor-cli", "editor-devcheck"].contains(&role) {
            continue;
        }
        if let Some(deps) = node["deps"].as_array() {
            for dep in deps {
                let Some(package) = dep["pkg"].as_str().and_then(|id| names.get(id)).copied()
                else {
                    v.push(Violation::new(
                        "resolved-role",
                        None,
                        "Resolved dependency has no package identity",
                    ));
                    continue;
                };
                let production = dep["dep_kinds"]
                    .as_array()
                    .is_some_and(|kinds| kinds.iter().any(|k| k["kind"].as_str() != Some("dev")));
                let allowed = match role {
                    "editor-core" => [
                        "serde",
                        "serde_json",
                        "schemars",
                        "serde_jcs",
                        "sha2",
                        "rusqlite",
                        "png",
                    ]
                    .contains(&package),
                    "editor-cli" => ["editor-core", "serde", "serde_json", "schemars", "sha2"]
                        .contains(&package),
                    _ => !["editor-core", "editor-cli"].contains(&package),
                };
                if (production || role == "editor-devcheck") && !allowed {
                    v.push(Violation::new(
                        "resolved-role",
                        None,
                        format!("{role} dependency alias resolves to illegal {package}"),
                    ));
                }
            }
        }
    }
    let mut queue: Vec<_> = names
        .iter()
        .filter(|(_, name)| ["editor-core", "editor-cli"].contains(name))
        .map(|(id, _)| *id)
        .collect();
    let mut seen = BTreeSet::new();
    while let Some(id) = queue.pop() {
        if !seen.insert(id) {
            continue;
        }
        if let Some(name) = names.get(id) {
            if banned(name) {
                v.push(Violation::new(
                    "resolved-backend",
                    None,
                    format!("Banned runtime package {name}"),
                ));
            }
        }
        if let Some(node) = nodes.iter().find(|n| n["id"].as_str() == Some(id)) {
            if let Some(deps) = node["deps"].as_array() {
                for d in deps {
                    if d["dep_kinds"]
                        .as_array()
                        .is_some_and(|a| a.iter().any(|k| k["kind"].as_str() != Some("dev")))
                    {
                        if let Some(id) = d["pkg"].as_str() {
                            queue.push(id)
                        }
                    }
                }
            }
        }
    }
    v
}
pub fn ledger(value: &Value, root: &Path) -> Vec<Violation> {
    let mut v = vec![];
    let Some(features) = value["capabilities"].as_array() else {
        return vec![Violation::new(
            "ledger-shape",
            None,
            "Capabilities must be an array",
        )];
    };
    let top = [
        "schemaVersion",
        "baseline",
        "checkedOn",
        "coverage",
        "capabilities",
        "referencePolicy",
    ];
    if value
        .as_object()
        .is_none_or(|o| o.keys().any(|k| !top.contains(&k.as_str())))
    {
        v.push(Violation::new(
            "ledger-fields",
            None,
            "Unknown ledger fields",
        ));
    }
    let mut ids = BTreeMap::new();
    for f in features {
        let allowed = [
            "id",
            "area",
            "name",
            "owner",
            "module",
            "phase",
            "command",
            "state",
            "dependsOn",
            "acceptance",
            "source",
            "evidence",
            "sourceKind",
            "behaviorContract",
            "acceptanceCorpus",
            "acceptanceCaseIds",
            "layer",
            "optionalDependencies",
            "technologyCandidates",
        ];
        if f.as_object()
            .is_none_or(|o| o.keys().any(|k| !allowed.contains(&k.as_str())))
        {
            v.push(Violation::new(
                "ledger-fields",
                None,
                "Unknown capability fields",
            ));
        }
        let id = f["id"].as_str().unwrap_or("");
        if id.is_empty() || ids.insert(id, f).is_some() {
            v.push(Violation::new(
                "ledger-id",
                None,
                format!("Missing or duplicate ID {id}"),
            ));
        }
        if f["state"] == "verified" || f["evidence"].as_array().is_none_or(|e| !e.is_empty()) {
            v.push(Violation::new(
                "unsupported-promotion",
                None,
                format!("{id} claims trusted promotion or evidence"),
            ));
        }
        if !["planned", "implemented"].contains(&f["state"].as_str().unwrap_or("")) {
            v.push(Violation::new(
                "ledger-state",
                None,
                format!("Invalid state for {id}"),
            ));
        }
        let native = f["layer"] == "native";
        let owner = f["owner"].as_str().unwrap_or("");
        let legal_owner = if native {
            owner == "Rust"
        } else {
            f["layer"] == "application"
                && ["Effect", "UI", "Foldkit"].contains(&owner)
                && f["phase"] != "P0"
        };
        if !legal_owner {
            v.push(Violation::new(
                "ledger-layer",
                None,
                format!("Illegal owner/layer for {id}"),
            ));
        }
        if !["P0", "P1", "P2", "P3", "P4", "P5", "P6", "P7"]
            .contains(&f["phase"].as_str().unwrap_or(""))
        {
            v.push(Violation::new(
                "ledger-phase",
                None,
                format!("Invalid phase for {id}"),
            ));
        }
        if f["acceptanceCaseIds"]
            .as_array()
            .is_none_or(|a| a.is_empty() || a.iter().any(|c| c.as_str().is_none()))
            || f["behaviorContract"]
                .as_str()
                .is_none_or(|p| !root.join(p).is_file())
        {
            v.push(Violation::new(
                "ledger-contract",
                None,
                format!("Missing cases or contract for {id}"),
            ));
        }
    }
    fn visit<'a>(
        id: &'a str,
        ids: &BTreeMap<&'a str, &'a Value>,
        active: &mut BTreeSet<&'a str>,
        done: &mut BTreeSet<&'a str>,
        v: &mut Vec<Violation>,
    ) {
        if done.contains(id) {
            return;
        }
        if !active.insert(id) {
            v.push(Violation::new(
                "ledger-cycle",
                None,
                format!("Dependency cycle at {id}"),
            ));
            return;
        }
        let f = ids[id];
        if let Some(deps) = f["dependsOn"].as_array() {
            for d in deps {
                let dep = d.as_str().unwrap_or("");
                if let Some(parent) = ids.get(dep) {
                    if f["phase"].as_str() < parent["phase"].as_str()
                        || (f["layer"] == "native" && parent["layer"] != "native")
                    {
                        v.push(Violation::new(
                            "ledger-dependency",
                            None,
                            format!("Illegal dependency {id} -> {dep}"),
                        ));
                    }
                    visit(dep, ids, active, done, v);
                } else {
                    v.push(Violation::new(
                        "ledger-dependency",
                        None,
                        format!("Missing {dep}"),
                    ));
                }
            }
        } else {
            v.push(Violation::new(
                "ledger-dependency",
                None,
                format!("Missing dependency array {id}"),
            ));
        }
        active.remove(id);
        done.insert(id);
    }
    let mut done = BTreeSet::new();
    for id in ids.keys() {
        visit(id, &ids, &mut BTreeSet::new(), &mut done, &mut v)
    }
    v
}
pub fn negative_fixtures(root: &Path) -> Vec<Violation> {
    let mut v = vec![];
    let fixtures = root.join("crates/editor-devcheck/tests/fixtures");
    for (name, role, reject) in [
        ("nested-core-process.rs", "editor-core", true),
        ("cfg-disabled-cli-process.rs", "editor-cli", true),
        ("legal-control.rs", "editor-core", false),
    ] {
        let path = fixtures.join(name);
        match fs::read_to_string(&path) {
            Ok(source) => {
                let (found, _) = analyze_source(role, &path, &source);
                if found.is_empty() == reject {
                    v.push(Violation::new(
                        "negative-source-fixture",
                        Some(path.display().to_string()),
                        "Fixture did not reach its required analyzer result",
                    ));
                }
            }
            Err(e) => v.push(Violation::new(
                "fixture-read",
                Some(path.display().to_string()),
                e.to_string(),
            )),
        }
    }
    for name in ["aliased-target-dependency.toml", "custom-build-path.toml"] {
        let path = fixtures.join(name);
        match fs::read_to_string(&path) {
            Ok(source) => {
                if analyze_manifest("editor-core", &path, &source).is_empty() {
                    v.push(Violation::new(
                        "negative-manifest-fixture",
                        Some(path.display().to_string()),
                        "Forbidden manifest fixture passed",
                    ));
                }
            }
            Err(e) => v.push(Violation::new(
                "fixture-read",
                Some(path.display().to_string()),
                e.to_string(),
            )),
        }
    }

    for(role,source,code) in [
        ("editor-core","mod nested { use std::process::Command as Runner; fn bad(){ Runner::new(\"sh\"); } }","runtime-process"),
        ("editor-cli","#[cfg(any())] mod side { use std::process as p; fn bad(){ p::Command::new(\"sh\"); } }","runtime-process"),
        ("editor-core","include!(\"external.rs\");","runtime-include"),
        ("editor-core","#[path=\"outside.rs\"] mod outside;","external"),
        ("editor-core","#[cfg_attr(unix,path=\"outside.rs\")] mod outside;","external"),
        ("editor-core","use std::*; fn f(){process::Command::new(\"sh\");}","runtime-process"),
        ("editor-core","extern crate std as s; fn f(){s::process::Command::new(\"sh\");}","runtime-process"),
        ("editor-core","fn f(){::std::r#process::Command::new(\"sh\");}","runtime-process"),
    ] {let(found,external)=analyze_source(role,Path::new("fixture.rs"),source);if if code=="external" {external.is_empty()} else {!found.iter().any(|f|f.code==code)} {v.push(Violation::new("negative-fixture",None,format!("Missed {code}")));}}
    for text in ["[package]\nname='editor-core'\nbuild='tools/custom.rs'", "[package]\nname='editor-core'\n[target.'cfg(unix)'.dependencies]\ncodec={package='ffmpeg-next', version='1', optional=true}","[package]\nname='editor-core'\n[dependencies]\neditor-cli={path='../editor-cli'}"] {if analyze_manifest("editor-core",Path::new("fixture/Cargo.toml"),text).is_empty() {v.push(Violation::new("negative-fixture",None,"Missed illegal manifest"));}}
    for source in [
        "fn main(){ let command = \"make dinner\"; }",
        "fn main(){std::process::exit(0);}",
    ] {
        let role = if source.contains("exit") {
            "editor-cli"
        } else {
            "editor-core"
        };
        if !analyze_source(role, Path::new("legal.rs"), source)
            .0
            .is_empty()
        {
            v.push(Violation::new(
                "legal-control",
                None,
                "Rejected legal source",
            ));
        }
    }
    if let Ok(mut value) = fs::read(root.join("capabilities.json"))
        .and_then(|b| serde_json::from_slice::<Value>(&b).map_err(std::io::Error::other))
    {
        value["capabilities"][0]["state"] = "verified".into();
        value["capabilities"][0]["evidence"] = serde_json::json!([{"passed":true}]);
        if !ledger(&value, root)
            .iter()
            .any(|e| e.code == "unsupported-promotion")
        {
            v.push(Violation::new(
                "negative-fixture",
                None,
                "Forged promotion accepted",
            ));
        }
    }
    v
}
#[cfg(test)]
mod tests {
    use super::*;
    #[test]
    fn recursive_alias_and_disabled_policy() {
        assert!(negative_fixtures(
            Path::new(env!("CARGO_MANIFEST_DIR"))
                .parent()
                .unwrap()
                .parent()
                .unwrap()
        )
        .is_empty());
    }
    #[test]
    fn alias_chain_process_is_rejected() {
        let (v, _) = analyze_source(
            "editor-core",
            Path::new("nested.rs"),
            "use std as s; use s::process as p; use p::Command as X; fn f(){ X::new(\"sh\"); }",
        );
        assert!(v.iter().any(|v| v.code == "runtime-process"));
    }
}

pub fn external_sources(root: &Path) -> Vec<PathBuf> {
    let mut found = BTreeMap::new();
    for role in ["editor-core", "editor-cli", "editor-devcheck"] {
        let base = root.join("crates").join(role);
        let mut paths = vec![];
        for directory in ["src", "tests", "benches", "examples"] {
            let path = base.join(directory);
            if path.exists() {
                rust_files(&path, &mut paths, &mut vec![]);
            }
        }
        if let Ok(text) = fs::read_to_string(base.join("Cargo.toml")) {
            if let Ok(manifest) = text.parse::<toml::Value>() {
                if let Some(build) = manifest
                    .get("package")
                    .and_then(|p| p.get("build"))
                    .and_then(|p| p.as_str())
                {
                    paths.push(base.join(build));
                }
                for target in ["lib", "bin", "test", "bench", "example"] {
                    if let Some(value) = manifest.get(target) {
                        let targets = value
                            .as_array()
                            .cloned()
                            .unwrap_or_else(|| vec![value.clone()]);
                        for t in targets {
                            if let Some(p) = t.get("path").and_then(|p| p.as_str()) {
                                paths.push(base.join(p));
                            }
                        }
                    }
                }
            }
        }
        while let Some(path) = paths.pop() {
            let Ok(canonical) = fs::canonicalize(&path) else {
                continue;
            };
            if found.insert(canonical, path.clone()).is_some() {
                continue;
            }
            if let Ok(source) = fs::read_to_string(&path) {
                let (_, external) = analyze_source(role, &path, &source);
                paths.extend(external);
            }
        }
    }
    found.into_values().collect()
}
#[cfg(test)]
mod regression_tests {
    use super::*;
    fn fixture() -> PathBuf {
        let path = std::env::temp_dir().join(format!(
            "devcheck-policy-{}",
            std::time::SystemTime::now()
                .duration_since(std::time::UNIX_EPOCH)
                .unwrap()
                .as_nanos()
        ));
        for role in ["editor-core", "editor-cli", "editor-devcheck"] {
            let base = path.join("crates").join(role);
            fs::create_dir_all(base.join("src")).unwrap();
            fs::write(
                base.join("Cargo.toml"),
                format!("[package]\nname='{role}'\n"),
            )
            .unwrap();
            fs::write(base.join("src/lib.rs"), "").unwrap();
        }
        path
    }
    #[test]
    fn external_cfg_attr_and_extra_targets_use_real_files() {
        let root = fixture();
        let base = root.join("crates/editor-core");
        fs::write(
            base.join("src/lib.rs"),
            "#[cfg_attr(unix,path=\"../outside.rs\")] mod side;",
        )
        .unwrap();
        fs::write(
            base.join("outside.rs"),
            "use std::process::Command as Runner;",
        )
        .unwrap();
        assert!(runtime_sources(&root).iter().any(
            |v| v.code == "runtime-process" && v.path.as_ref().unwrap().ends_with("outside.rs")
        ));
        fs::write(base.join("src/lib.rs"), "").unwrap();
        fs::write(
            base.join("Cargo.toml"),
            "[package]\nname='editor-core'\n[[bin]]\nname='extra'\npath='outside.rs'",
        )
        .unwrap();
        assert!(runtime_sources(&root)
            .iter()
            .any(|v| v.code == "runtime-process"));
        fs::create_dir(base.join("tools")).unwrap();
        fs::write(
            base.join("tools/build-native.rs"),
            "fn main(){std::process::Command::new(\"ffmpeg\");}",
        )
        .unwrap();
        fs::write(
            base.join("Cargo.toml"),
            "[package]\nname='editor-core'\nbuild='tools/build-native.rs'",
        )
        .unwrap();
        assert!(runtime_sources(&root)
            .iter()
            .any(|v| v.code == "renderer-literal"));
        assert!(analyze_manifest(
            "editor-core",
            &base.join("Cargo.toml"),
            &fs::read_to_string(base.join("Cargo.toml")).unwrap()
        )
        .iter()
        .any(|v| v.code == "runtime-build"));
    }
    #[test]
    fn nested_development_process_owner_is_rejected() {
        let root = fixture();
        let directory = root.join("crates/editor-devcheck/src/other");
        fs::create_dir(&directory).unwrap();
        fs::write(directory.join("process.rs"), "use std::process::Command;").unwrap();
        assert!(runtime_sources(&root)
            .iter()
            .any(|v| v.code == "runtime-process"));
    }
    #[test]
    fn resolved_workspace_alias_cannot_invert_direction() {
        for (role, package, kind) in [
            ("editor-core", "editor-devcheck", Value::Null),
            (
                "editor-devcheck",
                "editor-core",
                Value::String("dev".into()),
            ),
        ] {
            let metadata = serde_json::json!({"packages":[{"id":"owner","name":role},{"id":"dep","name":package}],"resolve":{"nodes":[{"id":"owner","deps":[{"name":"serde","pkg":"dep","dep_kinds":[{"kind":kind}]}]},{"id":"dep","deps":[]}]}});
            assert!(dependencies(&metadata)
                .iter()
                .any(|v| v.code == "resolved-role"));
        }
    }
    #[test]
    fn dev_backend_and_verifier_runtime_edges_are_rejected() {
        for (role, package) in [
            ("editor-cli", "ffmpeg-next"),
            ("editor-devcheck", "editor-core"),
            ("editor-devcheck", "libav-sys"),
        ] {
            let text=format!("[package]\nname='{role}'\n[dev-dependencies]\ncodec={{package='{package}',version='1'}}");
            assert!(!analyze_manifest(role, Path::new("fixture/Cargo.toml"), &text).is_empty());
        }
    }
}

#[cfg(test)]
mod ownership_regressions {
    use super::*;
    #[test]
    fn implicit_root_member_is_rejected() {
        let root = std::env::temp_dir().join(format!(
            "devcheck-root-role-{}",
            std::time::SystemTime::now()
                .duration_since(std::time::UNIX_EPOCH)
                .unwrap()
                .as_nanos()
        ));
        fs::create_dir(&root).unwrap();
        fs::write(root.join("Cargo.toml"),"[workspace]\nmembers=['crates/editor-core','crates/editor-cli','crates/editor-devcheck']\n[package]\nname='unassigned'\nversion='0.1.0'").unwrap();
        assert!(ownership(&root)
            .iter()
            .any(|v| v.code == "workspace-root-package"));
        let metadata = serde_json::json!({"packages":[{"id":"root","name":"unassigned"},{"id":"core","name":"editor-core"},{"id":"cli","name":"editor-cli"},{"id":"dev","name":"editor-devcheck"}],"workspace_members":["root","core","cli","dev"],"resolve":{"nodes":[]}});
        assert!(dependencies(&metadata)
            .iter()
            .any(|v| v.code == "resolved-workspace-roles"));
    }
    #[test]
    fn external_development_process_is_rejected() {
        let root = std::env::temp_dir().join(format!(
            "devcheck-outside-owner-{}",
            std::time::SystemTime::now()
                .duration_since(std::time::UNIX_EPOCH)
                .unwrap()
                .as_nanos()
        ));
        for role in ["editor-core", "editor-cli", "editor-devcheck"] {
            fs::create_dir_all(root.join("crates").join(role).join("src")).unwrap();
        }
        let base = root.join("crates/editor-devcheck");
        fs::write(
            base.join("src/main.rs"),
            "#[path=\"../worker.rs\"] mod worker;",
        )
        .unwrap();
        fs::write(base.join("worker.rs"), "use std::process::Command;").unwrap();
        assert!(runtime_sources(&root).iter().any(
            |v| v.code == "runtime-process" && v.path.as_ref().unwrap().ends_with("worker.rs")
        ));
    }
}

#[cfg(test)]
mod alias_scope_regression {
    use super::*;
    #[test]
    fn unrelated_std_alias_cannot_hide_syntactic_standard_process() {
        let source="mod elsewhere { use crate::local_std as std; } mod local_std {} use std::r#process::Command as Runner; fn f(){Runner::new(\"sh\");}";
        assert!(analyze_source("editor-core", Path::new("outer.rs"), source)
            .0
            .iter()
            .any(|v| v.code == "runtime-process"));
    }
}
