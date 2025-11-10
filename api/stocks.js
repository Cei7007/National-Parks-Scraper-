/**
 * Serverless Function: Competitor Stock Data API
 *
 * This function fetches real-time stock prices for major technology companies
 * from the API Ninjas Stock Price endpoint. It serves as a secure backend proxy
 * to protect API credentials and format data for the business intelligence dashboard.
 *
 * @returns {Object} JSON response with stock data for all tracked companies
 */

// Configuration: Companies to track for competitive intelligence
const COMPANIES = [
  { ticker: 'AAPL', name: 'Apple Inc.' },
  { ticker: 'MSFT', name: 'Microsoft Corporation' },
  { ticker: 'GOOGL', name: 'Alphabet Inc. (Google)' },
  { ticker: 'META', name: 'Meta Platforms Inc.' },
  { ticker: 'AMZN', name: 'Amazon.com Inc.' }
];

const API_BASE_URL = 'https://api.api-ninjas.com/v1/stockprice';

/**
 * Fetches stock price data for a single ticker symbol
 *
 * @param {string} ticker - Stock ticker symbol (e.g., 'AAPL')
 * @param {string} apiKey - API authentication key
 * @returns {Promise<Object>} Stock price data
 */
async function fetchStockPrice(ticker, apiKey) {
  const url = `${API_BASE_URL}?ticker=${ticker}`;

  const response = await fetch(url, {
    headers: {
      'X-Api-Key': apiKey
    }
  });

  if (!response.ok) {
    throw new Error(`API request failed for ${ticker}: ${response.status} ${response.statusText}`);
  }

  return await response.json();
}

/**
 * Main serverless function handler
 * Vercel will automatically call this function when the endpoint is accessed
 */
export default async function handler(req, res) {
  // Set CORS headers to allow requests from any origin
  res.setHeader('Access-Control-Allow-Origin', '*');
  res.setHeader('Access-Control-Allow-Methods', 'GET, OPTIONS');
  res.setHeader('Access-Control-Allow-Headers', 'Content-Type');

  // Handle preflight OPTIONS request
  if (req.method === 'OPTIONS') {
    return res.status(200).end();
  }

  // Only allow GET requests
  if (req.method !== 'GET') {
    return res.status(405).json({
      error: 'Method not allowed',
      message: 'This endpoint only accepts GET requests'
    });
  }

  try {
    // Validate API key exists in environment variables
    const apiKey = process.env.API_KEY;

    if (!apiKey) {
      console.error('API_KEY environment variable is not configured');
      return res.status(500).json({
        error: 'Server configuration error',
        message: 'API key is not configured on the server'
      });
    }

    // Fetch stock data for all companies in parallel for optimal performance
    const stockPromises = COMPANIES.map(async (company) => {
      try {
        const data = await fetchStockPrice(company.ticker, apiKey);

        return {
          ticker: company.ticker,
          companyName: company.name,
          price: data.price || 0,
          success: true
        };
      } catch (error) {
        // Log individual stock fetch errors but don't fail the entire request
        console.error(`Error fetching ${company.ticker}:`, error.message);

        return {
          ticker: company.ticker,
          companyName: company.name,
          price: null,
          success: false,
          error: error.message
        };
      }
    });

    // Wait for all stock data requests to complete
    const stockData = await Promise.all(stockPromises);

    // Filter out any failed requests
    const successfulData = stockData.filter(stock => stock.success);

    if (successfulData.length === 0) {
      return res.status(503).json({
        error: 'Service unavailable',
        message: 'Unable to fetch stock data from the API. Please try again later.'
      });
    }

    // Return successful response with timestamp
    return res.status(200).json({
      success: true,
      timestamp: new Date().toISOString(),
      dataCount: successfulData.length,
      stocks: successfulData
    });

  } catch (error) {
    // Catch any unexpected errors
    console.error('Unexpected error in stocks API:', error);

    return res.status(500).json({
      error: 'Internal server error',
      message: 'An unexpected error occurred while processing your request'
    });
  }
}
