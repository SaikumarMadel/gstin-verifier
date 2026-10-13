# ZDN MIS Integration Guide: GST Auto-Fill Module

This directory contains the ready-to-use adapter files for integrating the private GST Verification Microservice into **ZDN MIS**.

---

## 1. File Placement in Monorepo

Copy the following files into your ZDN MIS backend:

```text
apps/api/src/integrations/gst/
├── gst-verification.interface.ts     <- Copy from this folder
├── gst-verification.adapter.ts       <- Copy from this folder
└── gst-verification.adapter.spec.ts  <- Copy from this folder
```

---

## 2. Environment Variable Configuration

Add the service URL to your `.env` in `apps/api/.env`:

```env
# URL to your private GST Verification microservice
GST_SERVICE_URL=http://localhost:5001

# Optional API Key (if configured in gst-integration/.env)
GST_SERVICE_API_KEY=
```

---

## 3. NestJS / Express Controller Integration

In `apps/api/src/modules/clients/clients.controller.ts`:

```typescript
import { Controller, Get, Post, Body, Param, HttpException, HttpStatus } from '@nestjs/common';
import { GstVerificationAdapter } from '../../integrations/gst/gst-verification.adapter';

@Controller('clients')
export class ClientsController {
  private readonly gstAdapter = new GstVerificationAdapter();

  /**
   * 1. Get Captcha for Modal Popover
   */
  @Get('verify-gst/captcha')
  async getCaptcha() {
    return await this.gstAdapter.getCaptcha();
  }

  /**
   * 2. Submit GSTIN + Captcha to Auto-Populate Client Form
   */
  @Post('verify-gst')
  async verifyGst(@Body() body: { sessionId: string; gstin: string; captcha: string }) {
    try {
      const taxpayer = await this.gstAdapter.verifyTaxpayer(
        body.sessionId,
        body.gstin,
        body.captcha,
      );

      return {
        success: true,
        client: {
          legalName: taxpayer.legalName,
          tradeName: taxpayer.tradeName,
          pan: taxpayer.pan,
          entityType: taxpayer.constitutionOfBusiness,
          industryVertical: taxpayer.primaryVertical,
          status: taxpayer.status,
          address: taxpayer.address.full,
          city: taxpayer.address.city,
          state: taxpayer.address.state,
          pinCode: taxpayer.address.pincode,
          einvoiceEnabled: taxpayer.compliance.einvoiceEnabled,
        },
      };
    } catch (error: any) {
      throw new HttpException(
        {
          error: error.errorCode || 'GST_VERIFICATION_FAILED',
          message: error.message,
        },
        error.statusCode || HttpStatus.BAD_REQUEST,
      );
    }
  }

  /**
   * 3. Instant Pre-validation (as user types)
   */
  @Get('verify-gst/validate/:gstin')
  async validateGstinLocally(@Param('gstin') gstin: string) {
    return await this.gstAdapter.validateGstinLocally(gstin);
  }
}
```

---

## 4. Frontend UX Workflow (React / Next.js)

```typescript
// Example: Client Creation Modal Hook
async function onGstinEntered(gstin: string) {
  // Step 1: Instant local validation (0ms)
  const validation = await api.get(`/clients/verify-gst/validate/${gstin}`);
  if (!validation.data.valid) {
    showToast("Invalid GSTIN format or checksum", "error");
    return;
  }

  // Step 2: Show Captcha Popover
  const captchaData = await api.get('/clients/verify-gst/captcha');
  openCaptchaModal({
    image: captchaData.data.captcha,
    sessionId: captchaData.data.sessionId,
    onSubmit: async (userEnteredCaptcha) => {
      // Step 3: Verify & Auto-fill
      const res = await api.post('/clients/verify-gst', {
        sessionId: captchaData.data.sessionId,
        gstin,
        captcha: userEnteredCaptcha,
      });

      // Step 4: Form fields populated!
      form.setValue('legalName', res.data.client.legalName);
      form.setValue('pan', res.data.client.pan);
      form.setValue('address', res.data.client.address);
      form.setValue('city', res.data.client.city);
      form.setValue('pinCode', res.data.client.pinCode);
      form.setValue('industryVertical', res.data.client.industryVertical);
      closeCaptchaModal();
      showToast("GST details auto-populated from government portal!", "success");
    }
  });
}
```

---

## 5. PostgreSQL Caching Strategy (Zero Duplicate Calls)

Store the raw JSON snapshot in your PostgreSQL `clients` table:

```sql
ALTER TABLE clients 
  ADD COLUMN IF NOT EXISTS gstin VARCHAR(15) UNIQUE,
  ADD COLUMN IF NOT EXISTS pan VARCHAR(10),
  ADD COLUMN IF NOT EXISTS gst_verified_at TIMESTAMP WITH TIME ZONE,
  ADD COLUMN IF NOT EXISTS gst_raw_metadata JSONB;
```

Before calling the GST portal, query:
```typescript
const existing = await clientRepo.findOne({ where: { gstin } });
if (existing && existing.gst_raw_metadata) {
  // Instant cache hit! No captcha needed!
  return existing.gst_raw_metadata;
}
```
