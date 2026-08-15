# 企業資料治理

本規約適用於 Ingest 前的原件、`raw/` 歸檔、`wiki/` Concept、視覺資產與其衍生內容。它是本倉的 producer-defined 治理擴充；不以 OKF 的 trust 欄位取代存取控制。

## 必填分類與責任

每個新建或實質更新的 Concept 必須在 frontmatter 宣告下列欄位；未知不可猜測。

| 欄位 | 允許值／格式 | 意義 |
|---|---|---|
| `classification` | `public` \| `internal` \| `confidential` \| `restricted` | 資料敏感度；不確定時先用較嚴格等級。 |
| `owner` | `team:<id>`、`human:<id>` 或 `process:<id>` | 對內容、來源與存取決策負責的角色。 |
| `access_scope` | `public` \| `organization` \| `team:<id>` \| `named:<approved-group>` | 允許閱覽的最小範圍；不得用此欄位取代 repo 權限。 |
| `contains_pii` | `true` \| `false` \| `unknown` | 是否含個人資料；未完成檢查即為 `unknown`。 |
| `retention` | `permanent` \| `until:<YYYY-MM-DD>` \| `per-policy:<id>` | 保存期限或適用政策。 |
| `redaction` | `none` \| `applied` \| `required` | 是否已遮罩，或尚需遮罩。 |

`owner` 不是作者；`generated.by` 記錄產生者，`verified` 記錄查核者。`classification` 與 `access_scope` 不應直接寫入姓名、帳號、客戶 ID、token 或其他敏感值。

## Git 准入規則

| 條件 | 可進 Git | 禁止進 Git |
|---|---|---|
| `public` + `contains_pii: false` + `redaction: none` | 已人工確認的 wiki、歸檔與必要視覺資產 | 秘密、憑證、production 匯出。 |
| `internal` + `contains_pii: false` | 僅在核准的私有 repo，且 owner 已確認的最小必要內容 | 公開 repo、未審查原件。 |
| `confidential` 或 `restricted` | 預設僅提交去識別的 wiki 摘要；原件存核准的受管制系統，repo 僅留可公開的來源識別／位置 | `raw/originals/`、`raw/sources/`、`raw/assets/` 的原內容，及任何可還原敏感資料的摘要。 |
| `contains_pii: true` 或 `unknown`，或 `redaction: required` | 完成遮罩與人工驗證後，才可提交不含 PII 的衍生內容 | 原件、截圖、OCR 文字、可逆遮罩、樣本資料與識別碼。 |

`raw/` 的「不可變」只表示已准入的歸檔不可就地改寫，不構成 Git 准入授權。不得以 hash、檔名、圖像裁切或註解繞過本表；秘密（password、API key、private key、session token）一律禁止進 Git，無論分類。

## CI 可驗證 gate

CI 執行 `uv run python scripts/governance-gate.py --base <base>`；初始分支或手動未給 base 時掃描所有 tracked/untracked 檔。它掃描常見秘密模式，並要求每一個新 `raw/` 檔在 `governance/raw-approvals.json` 有不含內容的核可 receipt。receipt 至少需含 `path`、`source_sha256`、`classification`、合法 `owner`、`approved_by: human:<id>`、ISO `approved_at`、`contains_pii: false` 與 `redaction: none`；digest 必須與實際內容一致。`confidential`／`restricted`、PII 或需遮罩的原件不可用 manifest 放行進 Git。

此 gate 是提交前的機械防線，不取代 DLP、repo ACL、人工判讀或完整 secret scanner。

## Ingest 前閘與人工驗證

1. 在複製原件或呼叫會將內容寫入 workspace 的工具前，判斷 classification、PII、owner、access scope 與 retention。
2. `confidential`、`restricted`、PII、未知 PII、含憑證或疑似受法規／合約限制的來源，必須停止自動 Ingest，交由 owner 或資料治理角色人工核可。
3. 核可者確認最小化、遮罩效果、Git 准入、保存位置與期限後，才可產生／提交衍生內容。若以 `verified` 表示此確認，必須用 `human:<id>` 並保留時間；不得把 LLM 自評當人審。
4. 對已提交內容的刪除或保留期限到期，由 owner 依事件處理；不可修改既有 `raw/`，應依資安／法遵程序撤除存取、輪替秘密並以新產物取代可公開版本。

## 例外

例外必須由 owner 與資料治理／資安核准，並在不含敏感內容的變更紀錄中載明：範圍、理由、核准者角色、到期日與補救措施。例外到期即失效；無到期日的例外無效。例外不得允許提交秘密、未遮罩 PII 或違反法律／合約的資料。

## 與 OKF v0.2 的關係

OKF `verified` 表示內容曾被確認，`status`／`stale_after` 表示生命週期；它們都不是 ACL 或資料分類。外部分享、匯出 bundle、建立 PR 前，仍須重新依本檔確認准入。
