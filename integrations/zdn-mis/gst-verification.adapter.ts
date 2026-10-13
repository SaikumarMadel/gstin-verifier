/**
 * ZDN MIS - GST Verification Adapter
 * Path: apps/api/src/integrations/gst/gst-verification.adapter.ts
 *
 * Implements Layer 2 Integration Adapter standard for ZDN MIS.
 * Connects to your private self-hosted GST microservice proxy.
 */

import axios, { AxiosInstance } from 'axios';
import {
  GstCaptchaResponse,
  GstVerificationResult,
  GstVerifiedTaxpayer,
  GstinValidationResult
} from './gst-verification.interface';

export class GstVerificationException extends Error {
  constructor(
    public readonly errorCode: string,
    message: string,
    public readonly statusCode: number = 400,
    public readonly details?: any
  ) {
    super(message);
    this.name = 'GstVerificationException';
  }
}

export class GstVerificationAdapter {
  private readonly client: AxiosInstance;
  private readonly baseUrl: string;

  constructor(serviceBaseUrl?: string, apiKey?: string) {
    this.baseUrl = serviceBaseUrl || process.env.GST_SERVICE_URL || 'http://localhost:5001';

    const headers: Record<string, string> = {
      'Content-Type': 'application/json',
      'Accept': 'application/json',
    };

    if (apiKey || process.env.GST_SERVICE_API_KEY) {
      headers['X-API-Key'] = apiKey || process.env.GST_SERVICE_API_KEY || '';
    }

    this.client = axios.create({
      baseURL: this.baseUrl,
      timeout: 15000, // 15 second request timeout
      headers,
    });
  }

  /**
   * Checks whether the GST microservice and government portal are online.
   * Use this to determine whether to present the 1-click auto-fill or fallback to manual typing.
   */
  async checkPortalStatus(): Promise<{ available: boolean; latencyMs?: number }> {
    try {
      const response = await this.client.get('/api/v1/portal-status');
      return {
        available: response.data.portalAvailable === true,
        latencyMs: response.data.latencyMs,
      };
    } catch {
      return { available: false };
    }
  }

  /**
   * Fetches a new captcha image and session ID.
   */
  async getCaptcha(): Promise<GstCaptchaResponse> {
    try {
      const response = await this.client.get('/api/v1/captcha');
      if (!response.data.success) {
        throw new GstVerificationException(
          response.data.error || 'CAPTCHA_FETCH_FAILED',
          response.data.message || 'Failed to fetch captcha'
        );
      }
      return {
        sessionId: response.data.sessionId,
        captcha: response.data.captcha,
        expiresIn: response.data.expiresIn || 300,
      };
    } catch (error: any) {
      this.handleAxiosError(error, 'Failed to fetch captcha from GST service');
    }
  }

  /**
   * Submits GSTIN and user-solved captcha to verify taxpayer and receive auto-populated client fields.
   */
  async verifyTaxpayer(sessionId: string, gstin: string, captcha: string): Promise<GstVerifiedTaxpayer> {
    try {
      const response = await this.client.post<GstVerificationResult>('/api/v1/verify', {
        sessionId,
        gstin: gstin.trim().toUpperCase(),
        captcha: captcha.trim(),
      });

      if (!response.data.success) {
        throw new GstVerificationException(
          'VERIFICATION_FAILED',
          'GST verification unsuccessful'
        );
      }

      return response.data.data;
    } catch (error: any) {
      this.handleAxiosError(error, 'GST verification failed');
    }
  }

  /**
   * Instant offline validation of GSTIN format and checksum.
   * Does not make external network requests to the government portal.
   */
  async validateGstinLocally(gstin: string): Promise<GstinValidationResult> {
    try {
      const response = await this.client.get(`/api/v1/gstin/${encodeURIComponent(gstin)}/validate`);
      return response.data.validation;
    } catch (error: any) {
      if (error.response?.data?.validation) {
        return error.response.data.validation;
      }
      return {
        valid: false,
        gstin,
        errors: [error.message || 'Validation request failed'],
      };
    }
  }

  private handleAxiosError(error: any, fallbackMessage: string): never {
    if (error instanceof GstVerificationException) {
      throw error;
    }

    if (error.response?.data) {
      const data = error.response.data;
      throw new GstVerificationException(
        data.error || 'API_ERROR',
        data.message || fallbackMessage,
        error.response.status,
        data.details || data.raw
      );
    }

    if (error.code === 'ECONNREFUSED' || error.code === 'ETIMEDOUT') {
      throw new GstVerificationException(
        'PORTAL_UNAVAILABLE',
        'GST service is unreachable. Please use manual client onboarding.',
        503
      );
    }

    throw new GstVerificationException('UNKNOWN_ERROR', error.message || fallbackMessage, 500);
  }
}
