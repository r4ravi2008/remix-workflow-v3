use editor_core::*;
use schemars::{schema_for, JsonSchema};
use serde::de::{MapAccess, SeqAccess, Visitor};
use serde::{Deserialize, Deserializer, Serialize};
use serde_json::{Map, Value};
use std::collections::BTreeMap;

#[derive(Debug, Serialize, Deserialize, JsonSchema)]
#[serde(untagged)]
pub enum SchemaHandshake {
    Hash(String),
    Discovery(()),
}
impl SchemaHandshake {
    pub fn as_deref(&self) -> Option<&str> {
        match self {
            Self::Hash(s) => Some(s),
            Self::Discovery(()) => None,
        }
    }
    pub fn is_some(&self) -> bool {
        self.as_deref().is_some()
    }
}
impl From<Option<String>> for SchemaHandshake {
    fn from(value: Option<String>) -> Self {
        match value {
            Some(s) => Self::Hash(s),
            None => Self::Discovery(()),
        }
    }
}

#[derive(Debug, Serialize, Deserialize, JsonSchema)]
#[serde(rename_all = "camelCase", deny_unknown_fields)]
pub struct Request<T> {
    pub protocol_version: u8,
    pub request_id: RequestId,
    pub expected_schema_sha256: SchemaHandshake,
    pub tool: String,
    pub input: T,
}
#[derive(Debug, Serialize, Deserialize, JsonSchema)]
#[serde(untagged)]
pub enum ErrorCorrelation {
    Known(RequestId),
    Unreadable(()),
}
impl From<Option<RequestId>> for ErrorCorrelation {
    fn from(value: Option<RequestId>) -> Self {
        match value {
            Some(id) => Self::Known(id),
            None => Self::Unreadable(()),
        }
    }
}

#[derive(Debug, Serialize, Deserialize, JsonSchema)]
#[serde(tag = "status", rename_all = "lowercase", deny_unknown_fields)]
pub enum Response<T> {
    Success {
        #[serde(rename = "protocolVersion")]
        protocol_version: u8,
        #[serde(rename = "requestId")]
        request_id: RequestId,
        #[serde(rename = "schemaSha256")]
        schema_sha256: String,
        replayed: bool,
        result: T,
    },
    Error {
        #[serde(rename = "protocolVersion")]
        protocol_version: u8,
        #[serde(rename = "requestId")]
        request_id: ErrorCorrelation,
        #[serde(rename = "schemaSha256")]
        schema_sha256: String,
        error: EditorError,
    },
}
#[derive(Clone, Debug, Serialize, Deserialize, JsonSchema)]
#[serde(deny_unknown_fields)]
pub struct Empty {}
#[derive(Clone, Debug, Serialize, Deserialize, JsonSchema)]
#[serde(deny_unknown_fields)]
pub struct ToolDescriptor {
    pub name: String,
    pub description: String,
}
#[derive(Clone, Debug, Serialize, Deserialize, JsonSchema)]
#[serde(rename_all = "camelCase", deny_unknown_fields)]
pub struct Capabilities {
    pub kernel_version: String,
    pub binary_sha256: String,
    pub protocol_version: u8,
    pub identity_version: u8,
    pub schema_sha256: String,
    pub tools: Vec<ToolDescriptor>,
    pub implemented_feature_ids: Vec<String>,
    pub limits: Limits,
}
#[derive(Clone, Debug, Serialize)]
#[serde(rename_all = "camelCase")]
pub struct ToolSchemas {
    pub name: String,
    pub input_schema: Value,
    pub output_schema: Value,
}

pub struct Registry {
    pub schemas: BTreeMap<String, ToolSchemas>,
    pub schema_sha256: String,
}
impl Registry {
    pub fn new() -> Result<Self, EditorError> {
        fn entry<I: JsonSchema, O: JsonSchema>(name: &str) -> ToolSchemas {
            ToolSchemas {
                name: name.into(),
                input_schema: serde_json::to_value(schema_for!(I)).expect("schema serializes"),
                output_schema: serde_json::to_value(schema_for!(Response<O>))
                    .expect("schema serializes"),
            }
        }
        let entries = [
            entry::<Empty, Capabilities>("engine.capabilities"),
            entry::<CreateProject, ProjectResult>("project.create"),
            entry::<InspectProject, Inspection>("project.inspect"),
            entry::<CommitProject, ProjectResult>("project.commit"),
            entry::<RenderFrame, ArtifactReceipt>("frame.render"),
            entry::<VerifyArtifact, Verification>("artifact.verify"),
        ];
        let schemas: BTreeMap<_, _> = entries.into_iter().map(|e| (e.name.clone(), e)).collect();
        #[derive(Serialize)]
        #[serde(rename_all = "camelCase")]
        struct Contract<'a> {
            protocol_version: u8,
            tools: Vec<&'a ToolSchemas>,
        }
        let schema_sha256 = structured_hash(&Contract {
            protocol_version: 1,
            tools: schemas.values().collect(),
        })?;
        Ok(Self {
            schemas,
            schema_sha256,
        })
    }
    pub fn capabilities(&self, binary_sha256: &str) -> Capabilities {
        Capabilities {
            kernel_version: VERSION.into(),
            binary_sha256: binary_sha256.into(),
            protocol_version: 1,
            identity_version: 1,
            schema_sha256: self.schema_sha256.clone(),
            tools: self
                .schemas
                .keys()
                .map(|name| ToolDescriptor {
                    name: name.clone(),
                    description: match name.as_str() {
                        "engine.capabilities" => "Discover compiled native tools and limits",
                        "project.create" => "Create an immutable revision-zero project",
                        "project.inspect" => "Read an immutable project snapshot",
                        "project.commit" => "Atomically apply typed clip edits",
                        "frame.render" => "Produce a source-bound CPU PNG frame",
                        _ => "Remeasure a registered artifact",
                    }
                    .into(),
                })
                .collect(),
            implemented_feature_ids: IMPLEMENTED_FEATURES.iter().map(|s| (*s).into()).collect(),
            limits: Limits::p0(),
        }
    }
}

struct StrictJson(Value);
impl<'de> Deserialize<'de> for StrictJson {
    fn deserialize<D: Deserializer<'de>>(deserializer: D) -> Result<Self, D::Error> {
        struct StrictVisitor;
        impl<'de> Visitor<'de> for StrictVisitor {
            type Value = StrictJson;
            fn expecting(&self, f: &mut std::fmt::Formatter) -> std::fmt::Result {
                f.write_str("JSON without duplicate keys or unsafe integers")
            }
            fn visit_bool<E: serde::de::Error>(self, v: bool) -> Result<Self::Value, E> {
                Ok(StrictJson(Value::Bool(v)))
            }
            fn visit_unit<E: serde::de::Error>(self) -> Result<Self::Value, E> {
                Ok(StrictJson(Value::Null))
            }
            fn visit_i64<E: serde::de::Error>(self, v: i64) -> Result<Self::Value, E> {
                if v.unsigned_abs() > MAX_SAFE_INTEGER {
                    return Err(E::custom("Integer exceeds the exact JavaScript range."));
                }
                Ok(StrictJson(v.into()))
            }
            fn visit_u64<E: serde::de::Error>(self, v: u64) -> Result<Self::Value, E> {
                if v > MAX_SAFE_INTEGER {
                    return Err(E::custom("Integer exceeds the exact JavaScript range."));
                }
                Ok(StrictJson(v.into()))
            }
            fn visit_f64<E: serde::de::Error>(self, v: f64) -> Result<Self::Value, E> {
                if !v.is_finite() || (v.fract() == 0.0 && v.abs() > MAX_SAFE_INTEGER as f64) {
                    return Err(E::custom("Nonfinite or unsafe JSON number."));
                }
                Ok(StrictJson(Value::Number(
                    serde_json::Number::from_f64(v).ok_or_else(|| E::custom("Invalid number."))?,
                )))
            }
            fn visit_str<E: serde::de::Error>(self, v: &str) -> Result<Self::Value, E> {
                Ok(StrictJson(v.into()))
            }
            fn visit_string<E: serde::de::Error>(self, v: String) -> Result<Self::Value, E> {
                Ok(StrictJson(v.into()))
            }
            fn visit_seq<A: SeqAccess<'de>>(self, mut seq: A) -> Result<Self::Value, A::Error> {
                let mut values = Vec::new();
                while let Some(value) = seq.next_element::<StrictJson>()? {
                    values.push(value.0);
                }
                Ok(StrictJson(Value::Array(values)))
            }
            fn visit_map<A: MapAccess<'de>>(self, mut map: A) -> Result<Self::Value, A::Error> {
                let mut values = Map::new();
                while let Some(key) = map.next_key::<String>()? {
                    if values.contains_key(&key) {
                        return Err(serde::de::Error::custom(format!(
                            "Duplicate JSON key: {key}"
                        )));
                    }
                    values.insert(key, map.next_value::<StrictJson>()?.0);
                }
                Ok(StrictJson(Value::Object(values)))
            }
        }
        deserializer.deserialize_any(StrictVisitor)
    }
}
pub fn parse(bytes: &[u8]) -> Result<Value, EditorError> {
    if bytes.len() > Limits::p0().input_bytes {
        return Err(EditorError::invalid("Request exceeds 1 MiB."));
    }
    serde_json::from_slice::<StrictJson>(bytes)
        .map(|v| v.0)
        .map_err(|e| EditorError::invalid(e.to_string()))
}
pub fn decode<T: serde::de::DeserializeOwned>(value: Value) -> Result<T, EditorError> {
    serde_json::from_value(value).map_err(|e| EditorError::invalid(e.to_string()))
}
pub fn command(tool: &str, input: Value) -> Result<Command, EditorError> {
    Ok(match tool {
        "project.create" => Command::CreateProject(decode(input)?),
        "project.inspect" => Command::InspectProject(decode(input)?),
        "project.commit" => Command::CommitProject(decode(input)?),
        "frame.render" => Command::RenderFrame(decode(input)?),
        "artifact.verify" => Command::VerifyArtifact(decode(input)?),
        _ => return Err(tool_error(tool)),
    })
}
pub fn tool_error(tool: &str) -> EditorError {
    let ledger: Value = serde_json::from_str(include_str!("../../../capabilities.json"))
        .expect("compiled capability ledger");
    let planned = ledger["capabilities"].as_array().is_some_and(|entries| {
        entries
            .iter()
            .any(|v| v["command"].as_str() == Some(tool) || v["id"].as_str() == Some(tool))
    });
    EditorError::new(
        if planned {
            ErrorCode::UnsupportedCapability
        } else {
            ErrorCode::UnknownTool
        },
        if planned {
            "This capability is planned and unavailable."
        } else {
            "This tool is not in the compiled registry."
        },
    )
}
pub fn progress(binary_sha256: &str, registry: &Registry) -> Value {
    let mut ledger: Value = serde_json::from_str(include_str!("../../../capabilities.json"))
        .expect("compiled capability ledger");
    if let Some(entries) = ledger["capabilities"].as_array_mut() {
        for entry in entries {
            entry["state"] =
                if IMPLEMENTED_FEATURES.contains(&entry["id"].as_str().unwrap_or_default()) {
                    "implemented"
                } else {
                    "planned"
                }
                .into();
            entry["evidence"] = Value::Array(vec![]);
            entry["unavailableReason"] = if entry["state"] == "planned" {
                "No compiled implementation.".into()
            } else {
                Value::Null
            };
        }
    }
    ledger["engine"] =
        serde_json::to_value(registry.capabilities(binary_sha256)).expect("capabilities serialize");
    ledger["verification"] = "No matching trusted acceptance evidence has been promoted.".into();
    ledger
}
