import logging
import io
from typing import Optional
from fastapi import UploadFile, HTTPException
import PyPDF2
from docx import Document

logger = logging.getLogger(__name__)

class FileProcessor:
    """파일 처리 서비스"""
    
    @staticmethod
    async def extract_text_from_file(file: UploadFile) -> str:
        """업로드된 파일에서 텍스트 추출"""
        try:
            # 파일 확장자 확인
            file_extension = file.filename.lower().split('.')[-1] if file.filename else ''
            
            if file_extension == 'pdf':
                return await FileProcessor._extract_text_from_pdf(file)
            elif file_extension in ['docx', 'doc']:
                return await FileProcessor._extract_text_from_docx(file)
            else:
                raise HTTPException(
                    status_code=400, 
                    detail="지원하지 않는 파일 형식입니다. PDF 또는 DOCX 파일을 업로드해주세요."
                )
                
        except HTTPException:
            raise
        except Exception as e:
            logger.error(f"파일 텍스트 추출 실패: {e}")
            raise HTTPException(
                status_code=500, 
                detail="파일 처리 중 오류가 발생했습니다."
            )
    
    @staticmethod
    async def _extract_text_from_pdf(file: UploadFile) -> str:
        """PDF 파일에서 텍스트 추출"""
        try:
            # 파일 내용 읽기
            content = await file.read()
            
            # PDF 리더 생성
            pdf_reader = PyPDF2.PdfReader(io.BytesIO(content))
            
            # 모든 페이지의 텍스트 추출
            text = ""
            for page in pdf_reader.pages:
                text += page.extract_text() + "\n"
            
            if not text.strip():
                raise HTTPException(
                    status_code=400,
                    detail="PDF 파일에서 텍스트를 추출할 수 없습니다. 텍스트가 포함된 PDF 파일인지 확인해주세요."
                )
            
            return text.strip()
            
        except Exception as e:
            logger.error(f"PDF 텍스트 추출 실패: {e}")
            raise HTTPException(
                status_code=400,
                detail="PDF 파일 처리 중 오류가 발생했습니다."
            )
    
    @staticmethod
    async def _extract_text_from_docx(file: UploadFile) -> str:
        """DOCX 파일에서 텍스트 추출"""
        try:
            # 파일 내용 읽기
            content = await file.read()
            
            # DOCX 문서 로드
            doc = Document(io.BytesIO(content))
            
            # 모든 단락의 텍스트 추출
            text = ""
            for paragraph in doc.paragraphs:
                text += paragraph.text + "\n"
            
            if not text.strip():
                raise HTTPException(
                    status_code=400,
                    detail="DOCX 파일에서 텍스트를 추출할 수 없습니다."
                )
            
            return text.strip()
            
        except Exception as e:
            logger.error(f"DOCX 텍스트 추출 실패: {e}")
            raise HTTPException(
                status_code=400,
                detail="DOCX 파일 처리 중 오류가 발생했습니다."
            )
    
    @staticmethod
    def validate_file(file: UploadFile) -> bool:
        """파일 유효성 검사"""
        if not file.filename:
            return False
        
        # 파일 크기 제한 (10MB)
        if hasattr(file, 'size') and file.size > 10 * 1024 * 1024:
            return False
        
        # 지원하는 파일 형식 확인
        allowed_extensions = ['pdf', 'docx', 'doc']
        file_extension = file.filename.lower().split('.')[-1]
        
        return file_extension in allowed_extensions 