/**
 * ZDN MIS - GST Verification Integration Types
 * Path: apps/api/src/integrations/gst/gst-verification.interface.ts
 */

export interface GstCaptchaResponse {
  sessionId: string;
  captcha: string; // Base64 data URI: data:image/png;base64,...
  expiresIn: number; // TTL in seconds (e.g. 300)
}

export interface GstAddress {
  full: string;
  pincode: string | null;
  city: string | null;
  state: string | null;
}

export interface GstStateMeta {
  code: string;
  name: string | null;
  shortCode: string | null;
}

export interface GstJurisdiction {
  state: string | null;
  center: string | null;
}

export interface GstComplianceInfo {
  einvoiceEnabled: boolean;
  aadhaarAuthenticated: boolean;
  fieldVisitConducted: boolean;
}

export interface GstVerifiedTaxpayer {
  gstin: string;
  legalName: string;
  tradeName: string;
  pan: string; // Characters 3-12 extracted from GSTIN
  status: string; // e.g. "Active", "Cancelled", "Suspended"
  isActive: boolean;
  constitutionOfBusiness: string; // e.g. "Private Limited Company", "Partnership", "Proprietorship"
  taxpayerType: string; // e.g. "Regular", "Composition"
  registrationDate: string | null; // "DD/MM/YYYY"
  cancellationDate: string | null;
  address: GstAddress;
  natureOfBusiness: string[];
  primaryVertical: string | null;
  state: GstStateMeta;
  jurisdiction: GstJurisdiction;
  compliance: GstComplianceInfo;
}

export interface GstVerificationResult {
  success: boolean;
  data: GstVerifiedTaxpayer;
  raw?: Record<string, any>;
}

export interface GstinValidationResult {
  valid: boolean;
  gstin: string;
  pan?: string;
  stateCode?: string;
  stateName?: string;
  checksum?: {
    expected: string;
    actual: string;
    valid: boolean;
  };
  errors?: string[];
}
