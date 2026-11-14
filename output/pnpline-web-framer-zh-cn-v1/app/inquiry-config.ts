const configuredApi = process.env.NEXT_PUBLIC_INQUIRY_API_URL?.trim();
const consentVersion = process.env.NEXT_PUBLIC_INQUIRY_CONSENT_VERSION?.trim();
const privacyEmail = process.env.NEXT_PUBLIC_INQUIRY_PRIVACY_EMAIL?.trim();

const privacyOperator = process.env.NEXT_PUBLIC_INQUIRY_PRIVACY_OPERATOR?.trim();
const privacyRecipientNotice = process.env.NEXT_PUBLIC_INQUIRY_PRIVACY_RECIPIENT_NOTICE?.trim();

const privacyRetentionNotice = process.env.NEXT_PUBLIC_INQUIRY_PRIVACY_RETENTION_NOTICE?.trim();

function loadConfig() {
  if (!configuredApi) return null;
  const url = new URL(configuredApi);
  if (url.protocol !== "https:" || url.username || url.password || url.pathname !== "/v1/inquiries" ||
      url.search || url.hash || !consentVersion || !privacyEmail || !privacyOperator || !privacyRecipientNotice ||
      !privacyRetentionNotice ||
      !/^[^\s@,;?&#]+@[^\s@,;?&#]+\.[^\s@,;?&#]+$/.test(privacyEmail)) {
    throw new Error("Live inquiry requires an HTTPS /v1/inquiries URL, a consent version, and published privacy details.");
  }
  return { api: url.href, consentVersion, privacyEmail, privacyOperator, privacyRecipientNotice, privacyRetentionNotice };
}

export const inquiryConfig = loadConfig();
