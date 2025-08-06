"""
ImgBB Image Upload Integration
For NFT image hosting using imgbb.com
"""

import requests
import base64
import os
from flask import current_app

class ImgBBUploader:
    def __init__(self, api_key=None):
        self.api_key = api_key or os.environ.get('IMGBB_API_KEY')
        self.base_url = "https://api.imgbb.com/1/upload"
    
    def upload_image(self, image_file, name=None):
        """
        Upload image to ImgBB and return the image URL
        """
        if not self.api_key:
            raise ValueError("ImgBB API key is required. Please set IMGBB_API_KEY environment variable.")
        
        try:
            # Convert image to base64
            image_file.seek(0)  # Reset file pointer
            image_data = image_file.read()
            image_base64 = base64.b64encode(image_data).decode('utf-8')
            
            # Prepare upload data
            upload_data = {
                'key': self.api_key,
                'image': image_base64,
                'name': name or 'nft_image'
            }
            
            # Upload to ImgBB with timeout
            response = requests.post(self.base_url, data=upload_data, timeout=10)
            
            if response.status_code == 200:
                result = response.json()
                if result.get('success'):
                    return {
                        'success': True,
                        'url': result['data']['display_url'],  # Use display_url for direct image access
                        'page_url': result['data']['url'],     # Page URL
                        'delete_url': result['data']['delete_url']
                    }
                else:
                    return {
                        'success': False,
                        'error': result.get('error', {}).get('message', 'Upload failed')
                    }
            else:
                return {
                    'success': False,
                    'error': f'HTTP {response.status_code}: {response.text}'
                }
                
        except Exception as e:
            return {
                'success': False,
                'error': str(e)
            }
    
    def upload_file_path(self, file_path, name=None):
        """
        Upload image from file path to ImgBB
        """
        try:
            with open(file_path, 'rb') as f:
                return self.upload_image(f, name)
        except Exception as e:
            return {
                'success': False,
                'error': str(e)
            }

# Global uploader instance
imgbb_uploader = ImgBBUploader()