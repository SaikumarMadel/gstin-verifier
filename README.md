# GST Verification Microservice

> **High-Performance, 100% Free Government Proxy for Instant Indian GSTIN Verification & Business Profile Extraction**

A robust, enterprise-grade microservice built to eliminate third-party vendor fees (Karza, Surepass, Razorpay, Signzy) and automate taxpayer verification in seconds.

Whether used as a standalone microservice or integrated into enterprise platforms like ERPs, CRMs, etc. this service cuts onboarding time from 15 minutes of manual data entry down to 10 seconds.

---

## 🌟 Why This Exists

Commercial GST verification APIs charge **₹1.50 to ₹3.50 per call** with steep monthly minimum commitments. This service acts as a private, high-speed proxy directly to the official GST Government Portal (`services.gst.gov.in`), completely free with zero subscription fees.

### Key Enhancements over `shubham-dube/GST-Verification-API`

| Capability | Reference Repo | ZDN GST Microservice |
|---|---|---|
| **Memory Management** | Unbounded Python dict (leaks memory) | **Thread-safe `SessionStore` with 5-min TTL auto-cleanup** |
| **Output Format** | Cryptic raw gov JSON (`lgnm`, `pradr.adr`) | **Typed, normalized DTO directly mapped to ZDN MIS models** |
| **PAN Extraction** | Manual parsing needed | **Instant automatic PAN extraction (chars 3–12)** |
| **Address Normalization** | Single unparsed string | **Separates Pincode, City, State, and Full Registered Address** |
| **Local Pre-Validation** | None (wastes portal captcha attempts) | **0ms offline regex + Modulo-36 check digit validation** |
| **Timeout Protection** | None (can hang threads indefinitely) | **Configurable timeouts (default 12s) & connection pooling** |
| **Government Error Mapping** | Generic error messages | **Accurate detection of `SWEB_9034` (captcha), `SWEB_9035` (invalid GST)** |
| **UI Testbench** | None | **Live Glassmorphic Developer Playground with live Captcha widget** |
| **Monorepo Adapter** | None | **Ready-to-copy TypeScript adapter + unit tests for ZDN MIS** |
| **Backwards Compatibility** | N/A | **100% compatible with `/api/v1/getCaptcha` and `/api/v1/getGSTDetails`** |

---

## 📦 What Data Gets Auto-Populated

A single 15-character GSTIN (e.g., `27AABCR1718E1ZP`) returns:

```json
{
  "gstin": "27AABCR1718E1ZP",
  "legalName": "RELIANCE RETAIL LIMITED",
  "tradeName": "RELIANCE RETAIL LIMITED",
  "pan": "AABCR1718E",
  "status": "Active",
  "isActive": true,
  "constitutionOfBusiness": "Public Limited Company",
  "taxpayerType": "Regular",
  "registrationDate": "01/07/2017",
  "address": {
    "full": "Reliance Corporate Park, TTC Industrial Area, Ghansoli, Navi Mumbai, Thane, Maharashtra, 400701",
    "pincode": "400701",
    "city": "Navi Mumbai",
    "state": "Maharashtra"
  },
  "natureOfBusiness": ["Retail Business", "Supplier of Services"],
  "primaryVertical": "Retail Business",
  "state": {
    "code": "27",
    "name": "Maharashtra",
    "shortCode": "MH"
  },
  "compliance": {
    "einvoiceEnabled": true,
    "aadhaarAuthenticated": true,
    "fieldVisitConducted": false
  }
}
```

---

## 🚀 Quick Start

### 1. Run Locally (Python 3.11+)

```bash
# Clone and enter directory
cd d:/ZDN/gst-integration

# Install dependencies
pip install -r requirements.txt

# Start the server
python run.py
```

The service will start at:
* 🌐 **Interactive Testbench & Playground:** `http://localhost:5001`
* 🩺 **Health Check & Latency Ping:** `http://localhost:5001/health`

### 2. Run with Docker / Docker Compose

```bash
docker compose up -d
```

---

## 📡 API Endpoints

### 1. `GET /api/v1/captcha`
Fetches a fresh visual Captcha image from the government portal and initializes a TTL session.

**Response (200 OK):**
```json
{
  "success": true,
  "sessionId": "4f18b3cb-3ea8-48be-8f81-54c37f4019a2",
  "captcha": "data:image/png;base64,iVBORw0KGgo...",
  "expiresIn": 300
}
```

---

### 2. `POST /api/v1/verify`
Submits the GSTIN and solved Captcha to query the portal.

**Request Body:**
```json
{
  "sessionId": "4f18b3cb-3ea8-48be-8f81-54c37f4019a2",
  "gstin": "27AABCR1718E1ZP",
  "captcha": "350958"
}
```

**Response (200 OK):**
Returns `{ "success": true, "data": { ...normalized... }, "raw": { ...raw government payload... } }`.

---

### 3. `GET /api/v1/gstin/:gstin/validate`
Instant local syntax and Modulo-36 checksum check. Zero external network calls.

---

### 4. Legacy Endpoints (Compatibility Mode)
* `GET /api/v1/getCaptcha`: Returns `{ "sessionId": "...", "image": "data:..." }`
* `POST /api/v1/getGSTDetails`: Accepts `{ "sessionId": "...", "GSTIN": "...", "captcha": "..." }` and returns the raw government JSON.

---

## 🔗 ZDN MIS Integration

See the complete guide and ready-to-use TypeScript adapter in:
👉 [`integrations/zdn-mis/README.md`](integrations/zdn-mis/README.md)

Files provided:
* [`gst-verification.interface.ts`](integrations/zdn-mis/gst-verification.interface.ts)
* [`gst-verification.adapter.ts`](integrations/zdn-mis/gst-verification.adapter.ts)
* [`gst-verification.adapter.spec.ts`](integrations/zdn-mis/gst-verification.adapter.spec.ts)

---

## 🧪 Testing

Run the test suite:

```bash
pytest tests/ -v
```

All 14 unit and integration tests validate:
- Format & state code validation
- Modulo-36 check digit calculations
- Normalizer & address parsing
- Session management & error code mappings
