/**
 * Unit tests for GstVerificationAdapter (Jest / Vitest)
 * Path: apps/api/src/integrations/gst/gst-verification.adapter.spec.ts
 */

import { GstVerificationAdapter, GstVerificationException } from './gst-verification.adapter';
import axios from 'axios';

jest.mock('axios');
const mockedAxios = axios as jest.Mocked<typeof axios>;

describe('GstVerificationAdapter', () => {
  let adapter: GstVerificationAdapter;
  const mockAxiosInstance = {
    get: jest.fn(),
    post: jest.fn(),
  };

  beforeEach(() => {
    jest.clearAllMocks();
    (axios.create as jest.Mock).mockReturnValue(mockAxiosInstance);
    adapter = new GstVerificationAdapter('http://localhost:5001');
  });

  it('fetches captcha and returns session id', async () => {
    mockAxiosInstance.get.mockResolvedValueOnce({
      data: {
        success: true,
        sessionId: 'session-1234',
        captcha: 'data:image/png;base64,sample',
        expiresIn: 300,
      },
    });

    const result = await adapter.getCaptcha();
    expect(result.sessionId).toBe('session-1234');
    expect(result.captcha).toContain('base64');
    expect(mockAxiosInstance.get).toHaveBeenCalledWith('/api/v1/captcha');
  });

  it('verifies taxpayer and returns normalized client profile', async () => {
    const mockClientData = {
      gstin: '27AABCR1718E1ZP',
      legalName: 'RELIANCE RETAIL LIMITED',
      tradeName: 'RELIANCE RETAIL LIMITED',
      pan: 'AABCR1718E',
      status: 'Active',
      isActive: true,
      constitutionOfBusiness: 'Public Limited Company',
      address: {
        full: 'Reliance Corporate Park, Ghansoli, Navi Mumbai, 400701',
        city: 'Navi Mumbai',
        state: 'Maharashtra',
        pincode: '400701',
      },
      natureOfBusiness: ['Retail Business'],
      primaryVertical: 'Retail Business',
    };

    mockAxiosInstance.post.mockResolvedValueOnce({
      data: {
        success: true,
        data: mockClientData,
      },
    });

    const result = await adapter.verifyTaxpayer('session-1234', '27AABCR1718E1ZP', '123456');
    expect(result.legalName).toBe('RELIANCE RETAIL LIMITED');
    expect(result.pan).toBe('AABCR1718E');
    expect(result.address.pincode).toBe('400701');
  });

  it('throws typed GstVerificationException on invalid captcha', async () => {
    mockAxiosInstance.post.mockRejectedValueOnce({
      response: {
        status: 400,
        data: {
          success: false,
          error: 'INVALID_CAPTCHA',
          message: 'The captcha entered was incorrect or expired.',
        },
      },
    });

    await expect(
      adapter.verifyTaxpayer('session-1234', '27AABCR1718E1ZP', '000000')
    ).rejects.toThrow(GstVerificationException);
  });
});
