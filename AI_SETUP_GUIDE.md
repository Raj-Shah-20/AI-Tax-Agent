# 🤖 AI Tax Advisor Setup Guide

## Quick Setup (5 minutes)

The AI Tax Advisor features require an OpenAI API key to function. Without this key, you'll see standard tax advice instead of personalized AI recommendations.

### Step 1: Get an OpenAI API Key
1. Go to https://platform.openai.com/api-keys
2. Sign up or log in to your OpenAI account
3. Click "Create new secret key"
4. Copy the key (starts with `sk-...`)

### Step 2: Set the Environment Variable

**Windows (PowerShell):**
```powershell
$env:OPENAI_API_KEY="your_api_key_here"
```

**macOS/Linux:**
```bash
export OPENAI_API_KEY="your_api_key_here"
```

### Step 3: Restart the Application
```bash
python app.py
```

## 💰 API Costs

OpenAI API usage is pay-per-use:
- **GPT-3.5-turbo**: ~$0.001-0.002 per tax calculation
- **Monthly cost**: $1-5 for typical usage
- **Free tier**: $5 credit for new accounts

## 🔍 AI Features

Once configured, you'll see these AI-powered sections in tax results:

### 🤖 AI Tax Advisor Insights
- Personalized advice based on your tax profile
- Smart recommendations for your income level
- Context-aware tax strategies

### 💡 Enhanced Deduction Opportunities
- AI-detected missed deductions
- Personalized opportunity analysis
- Income-specific recommendations

### 🚀 Advanced Optimization Tips
- AI-generated tax planning strategies
- Timing recommendations
- Advanced tax optimization techniques

## 🛠️ Troubleshooting

### Issue: "API key not found"
**Solution**: Set the `OPENAI_API_KEY` environment variable as shown above.

### Issue: "API quota exceeded"
**Solution**: Check your OpenAI account billing and add credits if needed.

### Issue: AI advice not appearing in web interface
**Solution**: 
1. Restart the Flask application
2. Clear browser cache and try again

## 🔐 Security Best Practices

1. **Never commit API keys to version control**
2. **Use environment variables only**
3. **Regenerate keys if compromised**
4. **Monitor API usage regularly**

---

**Ready to see AI tax advice in action?** Set up your API key and restart the application! 