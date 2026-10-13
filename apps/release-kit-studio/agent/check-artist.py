"""Exercise artist isolation and revision conflicts against native local D1."""
import json
from pathlib import Path
import time
import urllib.error
import urllib.request

APP = Path(__file__).resolve().parent.parent
BASE = "http://localhost:1337"


def main():
    operator = next(
        line.split("=", 1)[1]
        for line in (APP / ".env").read_text().splitlines()
        if line.startswith("STUDIO_OPERATOR_TOKEN=")
    )

    def call(path, method="GET", body=None, session=None, privileged=False):
        headers = {"Origin": BASE}
        if session:
            headers["Cookie"] = session
        if privileged:
            headers["Authorization"] = "Bearer " + operator
        data = None
        if body is not None:
            headers["Content-Type"] = "application/json"
            data = json.dumps(body).encode()
        request = urllib.request.Request(BASE + path, data=data, method=method, headers=headers)
        try:
            with urllib.request.urlopen(request, timeout=20) as response:
                return response.status, json.load(response), response.headers
        except urllib.error.HTTPError as error:
            return error.code, json.load(error), error.headers

    def sign_in(name):
        code, invitation, _ = call("/api/operator/invites", "POST", {"tenantName": name}, privileged=True)
        assert code == 201
        code, account, headers = call("/api/auth/exchange", "POST", {"token": invitation["token"]})
        assert code == 200
        return account["tenant"]["id"], headers["Set-Cookie"].split(";", 1)[0]

    tenant, session = sign_in("Artist profile native diagnostic")
    _, other = sign_in("Artist profile isolation diagnostic")
    assert call("/api/artist-profile")[0] == 401
    assert call("/api/artist-profile", session=session)[1] == {"artist": None}
    profile = {
        "name": "Diagnostic artist",
        "identity": "Recurring river environments with native Telugu lyric art.",
        "palette": "River dusk",
        "intensity": "Restrained",
    }
    code, saved, _ = call("/api/artist-profile", "PUT", {"profile": profile, "expectedRevision": 0}, session)
    assert code == 200 and saved["artist"]["revision"] == 1
    assert call("/api/artist-profile", session=other)[1] == {"artist": None}
    changed = dict(profile, name="Updated diagnostic artist")
    code, updated, _ = call("/api/artist-profile", "PUT", {"profile": changed, "expectedRevision": 1}, session)
    assert code == 200 and updated["artist"]["revision"] == 2
    assert call("/api/artist-profile", "PUT", {"profile": profile, "expectedRevision": 1}, session)[0] == 409
    assert call("/api/artist-profile", "PUT", {"profile": profile, "expectedRevision": 0}, session)[0] == 409
    assert call("/api/artist-profile", "PUT", {"profile": dict(profile, name=""), "expectedRevision": 2}, session)[0] == 400
    assert call("/api/artist-profile", session=session)[1]["artist"] == updated["artist"]
    assert call("/api/auth/logout", "POST", {}, session)[0] == 200
    assert call("/api/artist-profile", session=session)[0] == 401
    code, invitation, _ = call("/api/operator/tenants/" + tenant + "/invites", "POST", {}, privileged=True)
    assert code == 201
    code, account, headers = call("/api/auth/exchange", "POST", {"token": invitation["token"]})
    assert code == 200 and account["tenant"]["id"] == tenant
    returned_session = headers["Set-Cookie"].split(";", 1)[0]
    assert call("/api/artist-profile", session=returned_session)[1]["artist"] == updated["artist"]
    assert call("/api/auth/exchange", "POST", {"token": invitation["token"]})[0] == 401
    assert call("/api/auth/logout", "POST", {}, returned_session)[0] == 200
    assert call("/api/auth/logout", "POST", {}, other)[0] == 200
    receipt = {
        "testedAt": time.time(), "runtime": "Alchemy native local D1",
        "tenantScopedArtistProfile": True, "initialRevision": 1, "updatedRevision": 2,
        "staleSaveRejected": True, "duplicateInitialSaveRejected": True,
        "invalidIdentityRejected": True, "signedOutSessionRejected": True,
        "returnInvitationPreservesStudioIdentity": True, "invitationReplayRejected": True,
        "diagnosticSessionsSignedOut": True, "diagnosticCredentialsPersisted": False,
        "hostedProfileVerified": False,
    }
    (APP / "docs/artist-profile-receipt.json").write_text(json.dumps(receipt, indent=2) + "\n")
    print(json.dumps(receipt))


if __name__ == "__main__":
    main()
