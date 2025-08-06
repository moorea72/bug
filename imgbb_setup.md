# ImgBB Integration Setup Guide

## How to get ImgBB API Key

1. Visit https://api.imgbb.com/
2. Sign up for a free account
3. Go to your account dashboard
4. Copy your API key

## Environment Setup

Add your ImgBB API key to environment variables:

```bash
export IMGBB_API_KEY="your_api_key_here"
```

## Features

- **Primary Upload**: All NFT images upload to ImgBB.com for fast loading
- **Blue Tick Upload**: Verification badges also upload to ImgBB.com
- **Fallback System**: If ImgBB fails, images save locally
- **Success Messages**: Clear feedback when uploads succeed
- **Error Handling**: Proper error messages if uploads fail

## Usage

1. Access admin panel: `/admin/nfts-simple`
2. Add/edit NFTs with photo uploads
3. Images automatically upload to ImgBB.com
4. URLs are saved in database for fast loading

## Benefits

- Fast image loading from ImgBB CDN
- Reliable image hosting
- No local storage limitations
- Professional image URLs
- Backup to local storage if needed