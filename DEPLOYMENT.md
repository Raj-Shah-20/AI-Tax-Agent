# 🚀 Vercel Deployment Guide

This guide will help you deploy your AI Tax Agent to Vercel for free.

## 📋 Prerequisites

1. **GitHub Account**: Your code needs to be in a GitHub repository
2. **Vercel Account**: Sign up at [vercel.com](https://vercel.com) (free tier available)
3. **OpenAI API Key** (optional): For AI features from [OpenAI](https://platform.openai.com/api-keys)

## 🔧 Deployment Steps

### 1. Prepare Your Repository

Make sure your repository has these files:
- ✅ `index.py` (main Flask app)
- ✅ `vercel.json` (Vercel configuration)
- ✅ `requirements.txt` (Python dependencies)
- ✅ `templates/` directory with HTML files
- ✅ `tax_calculator.py` (core logic)

### 2. Deploy to Vercel

#### Option A: One-Click Deploy
[![Deploy with Vercel](https://vercel.com/button)](https://vercel.com/new/clone?repository-url=https://github.com/YOUR_USERNAME/ai-tax-agent)

#### Option B: Manual Deploy
1. Go to [vercel.com](https://vercel.com) and sign in
2. Click **"New Project"**
3. Import your GitHub repository
4. Vercel will auto-detect it's a Python project
5. Click **"Deploy"**

### 3. Configure Environment Variables

After deployment, set up environment variables:

1. Go to your project dashboard on Vercel
2. Click **"Settings"** → **"Environment Variables"**
3. Add these variables:

| Variable | Value | Required |
|----------|-------|----------|
| `OPENAI_API_KEY` | Your OpenAI API key | Optional (for AI features) |



### 4. Redeploy (if needed)

After adding environment variables:
1. Go to **"Deployments"**
2. Click **"Redeploy"** on the latest deployment

## 🔍 Vercel Configuration Details

### `vercel.json` Configuration
```json
{
  "version": 2,
  "builds": [
    { "src": "index.py", "use": "@vercel/python" }
  ],
  "routes": [
    { "src": "/(.*)", "dest": "index.py" }
  ]
}
```

### Key Changes for Vercel
- **Entry Point**: `index.py`
- **PDF Generation**: Uses in-memory PDF generation (serverless-compatible)
- **No File System**: Removed directory creation for generated forms
- **Environment Variables**: Uses `os.environ.get()` for configuration

## 📊 Vercel Features

### ✅ What Works
- ✅ Tax calculations with 2025 IRS brackets
- ✅ Input validation and error handling
- ✅ PDF form generation and download
- ✅ AI-powered tax advice (with API key)
- ✅ Responsive web interface
- ✅ Real-time form validation

### 🚫 Limitations
- **File Storage**: No persistent file storage (PDFs generated in memory)

## 🔐 Security Best Practices

1. **Environment Variables**: Never commit API keys to your repository
2. **HTTPS**: Vercel provides HTTPS by default
3. **Rate Limiting**: Consider implementing rate limiting for production use

## 🐛 Troubleshooting

### Common Issues

**❌ "Build Failed" Error**
- Check `requirements.txt` has all dependencies
- Ensure `index.py` exists in root directory

**❌ "Function Timeout" Error**
- Reduce PDF complexity or optimize AI calls

**❌ "Internal Server Error"**
- Check Vercel function logs in the dashboard
- Verify environment variables are set correctly

**❌ AI Features Not Working**
- Ensure `OPENAI_API_KEY` is set in environment variables
- Check OpenAI account has available credits

### Viewing Logs

1. Go to your project dashboard
2. Click **"Functions"** → **"View Function Logs"**
3. Look for error messages and stack traces

## 💰 Cost Considerations

### Vercel Costs (Free Tier)
- **Bandwidth**: 100GB/month
- **Function Execution**: 100GB-hours/month
- **Invocations**: 1M/month

### OpenAI API Costs
- **GPT-3.5-turbo**: ~$0.001-0.002 per tax calculation
- **Monthly**: $1-5 for typical usage
- **Free tier**: $5 credit for new accounts
