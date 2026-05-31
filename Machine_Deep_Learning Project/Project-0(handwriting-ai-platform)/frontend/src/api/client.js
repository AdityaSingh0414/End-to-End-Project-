const BASE_URL = 'http://localhost:5000/api';

export const apiClient = {
  predict: async ({ image, mode = 'auto', autocorrect = true, dilation = 1, splitRatio = 1.4, filename = 'canvas_draw.png' }) => {
    try {
      const response = await fetch(`${BASE_URL}/predict`, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify({
          image,
          mode,
          autocorrect,
          dilation,
          split_ratio: splitRatio,
          filename,
        }),
      });
      
      if (!response.ok) {
        const errorData = await response.json();
        throw new Error(errorData.error || 'Prediction failed');
      }
      
      return await response.json();
    } catch (error) {
      console.error('API Client Error (predict):', error);
      throw error;
    }
  },

  getAnalytics: async () => {
    try {
      const response = await fetch(`${BASE_URL}/analytics`);
      if (!response.ok) {
        throw new Error('Failed to fetch analytics');
      }
      return await response.json();
    } catch (error) {
      console.error('API Client Error (getAnalytics):', error);
      throw error;
    }
  },

  clearLogs: async () => {
    try {
      const response = await fetch(`${BASE_URL}/clear-logs`, {
        method: 'POST',
      });
      if (!response.ok) {
        throw new Error('Failed to clear logs');
      }
      return await response.json();
    } catch (error) {
      console.error('API Client Error (clearLogs):', error);
      throw error;
    }
  },

  exportCSVUrl: `${BASE_URL}/export-csv`,
};
