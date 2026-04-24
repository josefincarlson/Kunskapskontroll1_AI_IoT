import json
import boto3

client=boto3.client('rekognition')
s3 = boto3.client('s3')

true_labels = {
    "IMG_2192.JPG": ["Straw", "Drinking Straw"],
    "IMG_2193.JPG": ["Battery"],
    "IMG_2194.JPG": ["Glasses Case", "Eyeglasses Case"],
    "IMG_2195.JPG": ["Hooks", "Metal Hooks"],
    "IMG_2196.JPG": ["Pens", "Pen"],
    "IMG_2197.JPG": ["Nail File"],
    "IMG_2198.JPG": ["Headphones"],
    "IMG_2199.JPG": ["Battery String Lights", "String Lights"],
    "IMG_2200.JPG": ["Glove"],
    "IMG_2201.JPG": ["Game Controller"],
    "IMG_2202.JPG": ["Glasses", "Sunglasses"],
    "IMG_2203.JPG": ["Remote Control"],
    "IMG_2204.JPG": ["Tealight", "Candle Holder"],
    "IMG_2205.JPG": ["Toy", "Stuffed Toy"],
    "IMG_2206.JPG": ["Ruler"],
    "IMG_2207.JPG": ["Scissors"],
    "IMG_2208.JPG": ["Toy Money", "Banknote", "Circuit Board"],
    "IMG_2209.JPG": ["Roll-On"],
    "IMG_2210.JPG": ["Eraser"],
    "IMG_2211.JPG": ["Rubik's Cube", "Toy", "Box"],
    "IMG_2212.JPG": ["Earbuds", "Headphones"],
    "IMG_2213.JPG": ["Keychain"],
    "IMG_2214.JPG": ["Medal"],
    "IMG_2215.JPG": ["Toy", "Toy Figures"],
    "IMG_2216.JPG": ["Cat", "Porcelain Cat", "Ornament Cat"],
    "IMG_2217.JPG": ["Dog", "Porcelain Dog", "Ornament Dog"],
    "IMG_2218.JPG": ["Soccer Ball"],
    "IMG_2219.JPG": ["Coin"],
    "IMG_2220.JPG": ["Bowl", "Snow Globe"],
    "IMG_2221.JPG": ["Bottle", "Prime Bottle"],
    "IMG_2222.JPG": ["Charger"],
    "IMG_2223.JPG": ["Cable"],
    "IMG_2224.JPG": ["Scrunchie", "Hair Tie"],
    "IMG_2225.JPG": ["Watch", "Wristwatch", "Jewelry"],
    "IMG_2226.JPG": ["Tape"],
    "IMG_2227.JPG": ["Keychain", "Lucky Charm", "Evil Eye", "Horseshoe"],
    "IMG_2228.JPG": ["Light Bulb"],
    "IMG_2229.JPG": ["Lens Cap", "Camera Lens Cap"],
    "IMG_2230.JPG": ["Pegboard", "Bead Board"],
    "IMG_2231.JPG": ["Dala Horse"],
    "IMG_2232.JPG": ["Knife"],
    "IMG_2233.JPG": ["Fork"],
    "IMG_2234.JPG": ["Spoon"],
    "IMG_2235.JPG": ["Egg Slicer"],
    "IMG_2236.JPG": ["Potato Peeler"],
    "IMG_2238.JPG": ["Stone"],
    "IMG_2239.JPG": ["Coaster", "Drink Coaster"],
    "IMG_2240.JPG": ["USB Flash Drive", "USB Stick"],
    "IMG_2241.JPG": ["Flower"],
    "IMG_2242.JPG": ["Chewing Gum Pack", "Gum Pack"],
    "IMG_2243.JPG": ["Speaker", "Computer Speaker"],
    "IMG_2244.JPG": ["Santa", "Beard", "Santa Hat", "Santa Decoration"],
    "IMG_2245.JPG": ["Bottle Opener"],
    "IMG_2246.JPG": ["Razor"]
}

def lambda_handler(event, context):
    bucket_name="aws-rekognition-picture-lables"
    results = []

    s3_response = s3.list_objects_v2(Bucket=bucket_name)

    if "Contents" not in s3_response:
        return {
            'statusCode': 200, 
            'body' : json.dumps("Inga filer hittades i bucket.", ensure_ascii=False)
        }

    for obj in s3_response['Contents']:
        image_name = obj['Key']
        print(image_name)

        if image_name.endswith('/'):
            continue

        if not image_name.lower().endswith(('.jpg', '.jpeg', '.png')):
            continue
        
        rekognition_response = client.detect_labels(
            Image={
                'S3Object': {
                    'Bucket': bucket_name,
                    'Name': image_name
                }
            },
            MaxLabels=10,
            MinConfidence=90
        )

        labels = []
        for label in rekognition_response['Labels']:
            labels.append({
                'Name': label['Name'],
                'Confidence': round(label['Confidence'], 2),
                'Parents': [parent['Name'] for parent in label.get('Parents', [])]
            })
        
        file_name = image_name.split('/')[-1]

        results.append({
            'image': image_name,
            'file_name': file_name,
            'true_labels': true_labels.get(file_name, []),
            'labels': labels
        })

    json_data = json.dumps(results, ensure_ascii=False, indent=2)

    s3.put_object(
        Bucket=bucket_name,
        Key='resultat/rekognition_resultat.json',
        Body=json_data.encode('utf-8'),
        ContentType='application/json'
    )

    return {
        'statusCode': 200,
        'body': json.dumps({
            'message': 'Klart',
            'antal_bilder': len(results),
            'json_fil': 'resultat/rekognition_resultat.json'
        }, ensure_ascii=False)
}