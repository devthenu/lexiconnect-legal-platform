export const normalizeError = (err, fallback = "Request failed.") => {
  if (!err) return fallback;
  if (typeof err === "string") return err;

  const detail = err?.detail;
  if (typeof detail === "string") return detail;

  if (err?.response?.data) {
    const responseData = err.response.data;
    if (typeof responseData === "string") return responseData;
    if (typeof responseData?.detail === "string") return responseData.detail;
    if (typeof responseData?.message === "string") return responseData.message;
    try {
      return JSON.stringify(responseData);
    } catch {
      return fallback;
    }
  }

  if (typeof err?.message === "string") return err.message;

  try {
    return JSON.stringify(err);
  } catch {
    return fallback;
  }
};

export const formatApiError = normalizeError;
