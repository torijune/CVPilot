#!/bin/bash

# AWS S3 + CloudFront 프론트엔드 배포 스크립트
set -e

# 설정
BUCKET_NAME="cvpilot-frontend"
REGION="us-east-1"
CLOUDFRONT_COMMENT="CVPilot Frontend Distribution"

echo "🚀 CVPilot 프론트엔드 S3 배포 시작..."

# 1. S3 버킷 생성 (존재하지 않으면)
echo "📦 S3 버킷 확인/생성 중..."
if ! aws s3api head-bucket --bucket $BUCKET_NAME 2>/dev/null; then
    echo "📦 S3 버킷 생성 중: $BUCKET_NAME"
    aws s3api create-bucket --bucket $BUCKET_NAME --region $REGION
    
    # 퍼블릭 액세스 차단 해제 (정적 웹사이트 호스팅용)
    aws s3api delete-public-access-block --bucket $BUCKET_NAME
    
    # 웹사이트 설정
    aws s3 website s3://$BUCKET_NAME --index-document index.html --error-document 404.html
    
    # 버킷 정책 설정 (퍼블릭 읽기 허용)
    cat > bucket-policy.json << EOF
{
    "Version": "2012-10-17",
    "Statement": [
        {
            "Sid": "PublicReadGetObject",
            "Effect": "Allow",
            "Principal": "*",
            "Action": "s3:GetObject",
            "Resource": "arn:aws:s3:::$BUCKET_NAME/*"
        }
    ]
}
EOF
    aws s3api put-bucket-policy --bucket $BUCKET_NAME --policy file://bucket-policy.json
    rm bucket-policy.json
else
    echo "✅ S3 버킷이 이미 존재합니다: $BUCKET_NAME"
fi

# 2. Next.js 빌드
echo "🏗️ Next.js 빌드 중..."
npm run build

# 3. S3에 업로드 (out 디렉토리 사용)
echo "📤 S3에 파일 업로드 중..."
if [ -d "out" ]; then
    aws s3 sync out s3://$BUCKET_NAME --delete
elif [ -d ".next" ]; then
    aws s3 sync .next/static s3://$BUCKET_NAME/_next/static --delete
    aws s3 cp .next/standalone s3://$BUCKET_NAME --recursive --exclude "node_modules/*"
fi

# public 디렉토리도 업로드
if [ -d "public" ]; then
    aws s3 sync public s3://$BUCKET_NAME --delete
fi

# 4. CloudFront 배포 확인/생성
echo "🌐 CloudFront 배포 확인 중..."
DISTRIBUTION_ID=$(aws cloudfront list-distributions --query "DistributionList.Items[?Comment=='$CLOUDFRONT_COMMENT'].Id" --output text 2>/dev/null || echo "")

if [ -z "$DISTRIBUTION_ID" ] || [ "$DISTRIBUTION_ID" == "None" ]; then
    echo "🌐 CloudFront 배포 생성 중..."
    
    # CloudFront 배포 설정
    cat > cloudfront-config.json << EOF
{
    "CallerReference": "cvpilot-$(date +%s)",
    "Comment": "$CLOUDFRONT_COMMENT",
    "DefaultCacheBehavior": {
        "TargetOriginId": "S3-$BUCKET_NAME",
        "ViewerProtocolPolicy": "redirect-to-https",
        "MinTTL": 0,
        "DefaultTTL": 86400,
        "MaxTTL": 31536000,
        "AllowedMethods": {
            "Quantity": 2,
            "Items": ["GET", "HEAD"],
            "CachedMethods": {
                "Quantity": 2,
                "Items": ["GET", "HEAD"]
            }
        },
        "ForwardedValues": {
            "QueryString": false,
            "Cookies": {
                "Forward": "none"
            }
        },
        "TrustedSigners": {
            "Enabled": false,
            "Quantity": 0
        },
        "Compress": true
    },
    "Origins": {
        "Quantity": 1,
        "Items": [
            {
                "Id": "S3-$BUCKET_NAME",
                "DomainName": "$BUCKET_NAME.s3-website-$REGION.amazonaws.com",
                "CustomOriginConfig": {
                    "HTTPPort": 80,
                    "HTTPSPort": 443,
                    "OriginProtocolPolicy": "http-only"
                }
            }
        ]
    },
    "Enabled": true,
    "DefaultRootObject": "index.html",
    "CustomErrorResponses": {
        "Quantity": 1,
        "Items": [
            {
                "ErrorCode": 404,
                "ResponsePagePath": "/404.html",
                "ResponseCode": "404",
                "ErrorCachingMinTTL": 300
            }
        ]
    }
}
EOF
    
    DISTRIBUTION_ID=$(aws cloudfront create-distribution --distribution-config file://cloudfront-config.json --query 'Distribution.Id' --output text)
    rm cloudfront-config.json
    
    echo "✅ CloudFront 배포 생성됨: $DISTRIBUTION_ID"
else
    echo "✅ CloudFront 배포가 이미 존재합니다: $DISTRIBUTION_ID"
fi

# 5. CloudFront 무효화 (캐시 갱신)
if [ ! -z "$DISTRIBUTION_ID" ] && [ "$DISTRIBUTION_ID" != "None" ]; then
    echo "🔄 CloudFront 캐시 무효화 중..."
    aws cloudfront create-invalidation --distribution-id $DISTRIBUTION_ID --paths "/*" > /dev/null
fi

# 6. URL 정보 출력
WEBSITE_URL="http://$BUCKET_NAME.s3-website-$REGION.amazonaws.com"
if [ ! -z "$DISTRIBUTION_ID" ] && [ "$DISTRIBUTION_ID" != "None" ]; then
    CLOUDFRONT_URL=$(aws cloudfront get-distribution --id $DISTRIBUTION_ID --query 'Distribution.DomainName' --output text)
fi

echo ""
echo "🎉 배포 완료!"
echo "📍 S3 Website URL: $WEBSITE_URL"
if [ ! -z "$CLOUDFRONT_URL" ]; then
    echo "🌐 CloudFront URL: https://$CLOUDFRONT_URL"
fi
echo ""
echo "⚠️  CloudFront 배포는 전파에 10-15분 정도 소요될 수 있습니다."
echo "" 