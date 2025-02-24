import pandas as pd
import json
import logging
from pathlib import Path

# Set up logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

def flatten_location(location):
    """Flatten location dictionary into separate columns"""
    if not location:
        return {
            'location_name': None,
            'address': None,
            'city': None,
            'state': None,
            'zip': None,
            'phone': None
        }
    
    return {
        'location_name': location.get('name'),
        'address': location.get('address'),
        'city': location.get('city'),
        'state': location.get('state'),
        'zip': location.get('zip'),
        'phone': location.get('phone')
    }

def flatten_reviews(reviews):
    """Convert reviews list to a string summary"""
    if not reviews:
        return None
        
    review_texts = []
    for review in reviews:
        author = review.get('author', {}).get('name', 'Anonymous')
        rating = review.get('reviewRating', {}).get('ratingValue', 'N/A')
        text = review.get('reviewBody', '').strip()
        review_texts.append(f"{author} ({rating}/5): {text}")
    
    return ' | '.join(review_texts)

def json_to_excel(json_file='activities_data.json', output_dir='data'):
    """Convert activities JSON data to Excel format"""
    try:
        # Create output directory if it doesn't exist
        output_path = Path(output_dir)
        output_path.mkdir(parents=True, exist_ok=True)
        
        # Set output file path
        output_file = output_path / 'activities.xlsx'
        
        # Check if file exists
        if not Path(json_file).exists():
            logger.error(f"Input file not found: {json_file}")
            return
            
        logger.info(f"Reading JSON file: {json_file}")
        
        # Read and validate JSON file
        with open(json_file, 'r', encoding='utf-8') as f:
            data = json.load(f)
            
        if not data:
            logger.error("JSON file is empty")
            return
            
        if not isinstance(data, list):
            logger.error("JSON data is not a list of activities")
            return
            
        logger.info(f"Found {len(data)} activities")
        logger.info(f"First activity: {data[0]['name'] if data else 'None'}")
        
        # Process each activity
        processed_data = []
        for activity in data:
            # Flatten location data
            location_data = flatten_location(activity.get('location'))
            
            # Process reviews
            reviews_text = flatten_reviews(activity.get('reviews'))
            
            # Create flattened record
            record = {
                'Position': activity.get('position'),
                'Name': activity.get('name'),
                'URL': activity.get('url'),
                'Email': activity.get('email'),
                'Description': activity.get('description'),
                'Image URL': activity.get('image_url'),
                'Image Filename': activity.get('image_filename'),
                'Location Name': location_data['location_name'],
                'Address': location_data['address'],
                'City': location_data['city'],
                'State': location_data['state'],
                'ZIP': location_data['zip'],
                'Phone': location_data['phone'],
                'Reviews': reviews_text,
                'Rating': activity.get('rating', {}).get('ratingValue') if activity.get('rating') else None
            }
            processed_data.append(record)
            
        # Convert to DataFrame
        df = pd.DataFrame(processed_data)
        
        # Sort by position
        df = df.sort_values('Position')
        
        # Save to Excel with auto-adjusted columns
        logger.info(f"Saving to Excel file: {output_file.absolute()}")
        with pd.ExcelWriter(output_file, engine='openpyxl') as writer:
            df.to_excel(writer, index=False, sheet_name='Activities')
            worksheet = writer.sheets['Activities']
            for idx, col in enumerate(df.columns):
                max_length = max(
                    df[col].astype(str).apply(len).max(),
                    len(str(col))
                )
                worksheet.column_dimensions[chr(65 + idx)].width = min(max_length + 2, 50)
        
        logger.info("Conversion completed successfully!")
        logger.info(f"Total activities processed: {len(processed_data)}")
        logger.info(f"Excel file saved to: {output_file.absolute()}")
        
    except Exception as e:
        logger.error(f"Error converting JSON to Excel: {str(e)}")
        raise

if __name__ == "__main__":
    json_to_excel() 