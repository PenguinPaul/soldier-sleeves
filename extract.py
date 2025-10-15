import requests
from bs4 import BeautifulSoup
import json

def extract_insignia_data(url):
	"""Extract insignia data from Army Institute of Heraldry page"""
	try:
		headers = {
			'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'
		}
		response = requests.get(url, headers=headers, verify=False)
		response.raise_for_status()
		soup = BeautifulSoup(response.content, 'html.parser')
		
		# Extract description
		description_span = soup.find('span', id='ContentPlaceHolder1_ucHeraldryDetails_ucHeraldryInfo_dlContent_lbContent_0')
		description = description_span.get_text(strip=True) if description_span else ""
		
		# Extract image URL
		img_tag = soup.find('img', title='Shoulder Sleeve Insignia')
		image_url = img_tag['src'] if img_tag else ""
		
		# Make image URL absolute if it's relative
		if image_url and not image_url.startswith('http'):
			from urllib.parse import urljoin
			image_url = urljoin(url, image_url)
		
		# Extract unit name (usually in a specific element, adjust as needed)
		# This may need adjustment based on actual page structure
		title_elem = soup.find('span', id='ContentPlaceHolder1_ucHeraldryDetails_ucHeraldryInfo_lblTitle')
		unit_name = title_elem.get_text(strip=True) if title_elem else "Unknown Unit"
		
		return {
			'description': description,
			'image': image_url,
			'name': unit_name,
			'link': url
		}
	except Exception as e:
		print(f"Error extracting data: {e}")
		return None

def get_user_input():
	"""Get user input for manual fields"""
	print("\n--- Enter Unit Details ---")
	name = input("Unit Name (or press Enter to use extracted): ").strip()
	nickname = input("Nickname: ").strip()
	shape = input("Shape (e.g., Shield, Circle, Triangle): ").strip()
	
	print("\nEnter colors (comma-separated, e.g., Red, White, Blue):")
	colors_input = input("Colors: ").strip()
	colors = [c.strip() for c in colors_input.split(',') if c.strip()]
	
	print("\nEnter features (comma-separated, e.g., Eagle, Star, Sword):")
	features_input = input("Features: ").strip()
	features = [f.strip() for f in features_input.split(',') if f.strip()]
	
	return {
		'name': name,
		'nickname': nickname,
		'shape': shape,
		'colors': colors,
		'features': features
	}

def format_javascript_object(data):
	"""Format data as JavaScript object literal"""
	# Escape quotes in strings
	def escape_str(s):
		return s.replace('\\', '\\\\').replace('"', '\\"').replace('\n', ' ')
	
	nickname_line = f'nickname: "{escape_str(data["nickname"])}",' if data['nickname'] else 'nickname: "",'
	
	js_obj = f"""			{{
				name: "{escape_str(data['name'])}",
				{nickname_line}
				description: "{escape_str(data['description'])}",
				shape: "{escape_str(data['shape'])}",
				features: [{', '.join(f'"{escape_str(f)}"' for f in data['features'])}],
				colors: [{', '.join(f'"{escape_str(c)}"' for c in data['colors'])}],
				image: "{escape_str(data['image'])}",
				link: "{escape_str(data['link'])}"
			}}"""
	
	return js_obj

def main():
	import urllib3
	urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)
	
	print("=== Army Institute of Heraldry Data Extractor ===\n")
	
	url = input("Enter Army Institute of Heraldry URL: ").strip()
	
	if not url:
		print("Error: URL is required")
		return
	
	print("\nExtracting data from URL...")
	extracted_data = extract_insignia_data(url)
	
	if not extracted_data:
		print("Failed to extract data from URL")
		return
	
	print(f"\nExtracted:")
	print(f"  Name: {extracted_data['name']}")
	print(f"  Description: {extracted_data['description'][:100]}...")
	print(f"  Image URL: {extracted_data['image']}")
	
	user_data = get_user_input()
	
	# Merge data
	final_data = {
		'name': user_data['name'] if user_data['name'] else extracted_data['name'],
		'nickname': user_data['nickname'],
		'description': extracted_data['description'],
		'shape': user_data['shape'],
		'features': user_data['features'],
		'colors': user_data['colors'],
		'image': extracted_data['image'],
		'link': extracted_data['link']
	}
	
	# Validate required fields (nickname is optional)
	if not all([final_data['name'], final_data['shape'], 
				final_data['colors'], final_data['features']]):
		print("\nError: All fields are required (name, shape, colors, features)")
		return
	
	print("\n" + "="*60)
	print("JavaScript object (copy and paste into your array):")
	print("="*60)
	print(format_javascript_object(final_data))
	print("="*60)
	
	# Also save to file
	with open('insignia_output.txt', 'w', encoding='utf-8') as f:
		f.write(format_javascript_object(final_data))
	print("\nOutput also saved to: insignia_output.txt")

if __name__ == "__main__":
	main()
