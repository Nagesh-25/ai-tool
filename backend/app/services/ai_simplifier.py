"""
AI-powered legal document simplification service using Google's Gemini API
"""

import logging
import json
import re
from typing import Dict, List, Any, Optional
import asyncio
from datetime import datetime

import google.generativeai as genai
from google.generativeai.types import HarmCategory, HarmBlockThreshold

from app.core.config import settings

logger = logging.getLogger(__name__)


class AISimplifier:
    """Service for simplifying legal documents using AI."""
    
    def __init__(self):
        self.model = None
        self._initialize_model()
    
    def _initialize_model(self):
        """Initialize the Gemini model."""
        try:
            # Configure the API key
            genai.configure(api_key=settings.GEMINI_API_KEY)
            
            # Initialize the model
            self.model = genai.GenerativeModel(
                model_name=settings.VERTEX_AI_MODEL_NAME,
                safety_settings={
                    HarmCategory.HARM_CATEGORY_HATE_SPEECH: HarmBlockThreshold.BLOCK_MEDIUM_AND_ABOVE,
                    HarmCategory.HARM_CATEGORY_DANGEROUS_CONTENT: HarmBlockThreshold.BLOCK_MEDIUM_AND_ABOVE,
                    HarmCategory.HARM_CATEGORY_SEXUALLY_EXPLICIT: HarmBlockThreshold.BLOCK_MEDIUM_AND_ABOVE,
                    HarmCategory.HARM_CATEGORY_HARASSMENT: HarmBlockThreshold.BLOCK_MEDIUM_AND_ABOVE,
                }
            )
            
            logger.info("Gemini model initialized successfully")
            
        except Exception as e:
            logger.error(f"Failed to initialize Gemini model: {e}")
            raise
    
    async def simplify_document(
        self, 
        text: str, 
        simplification_level: str = "standard",
        target_audience: str = "general_public"
    ) -> Dict[str, Any]:
        """
        Simplify a legal document using AI.
        
        Args:
            text: Original document text
            simplification_level: Level of simplification (basic, standard, detailed)
            target_audience: Target audience for simplification
            
        Returns:
            Dictionary containing simplified content and metadata
        """
        try:
            # Preprocess the text
            cleaned_text = self._preprocess_text(text)
            
            # Create the prompt based on simplification level and audience
            prompt = self._create_simplification_prompt(
                cleaned_text, simplification_level, target_audience
            )
            
            # Generate simplified content
            simplified_content = await self._generate_simplified_content(prompt)
            
            # Parse and structure the response
            structured_content = self._parse_ai_response(simplified_content)
            
            # Add metadata
            structured_content.update({
                "confidence_score": self._calculate_confidence_score(cleaned_text, structured_content),
                "reading_level": self._estimate_reading_level(structured_content.get("summary", "")),
                "processing_timestamp": datetime.utcnow().isoformat(),
                "simplification_level": simplification_level,
                "target_audience": target_audience
            })
            
            return structured_content
            
        except Exception as e:
            logger.error(f"Error simplifying document: {e}")
            raise
    
    def _preprocess_text(self, text: str) -> str:
        """Preprocess text for better AI processing."""
        # Remove excessive whitespace
        text = re.sub(r'\s+', ' ', text)
        
        # Remove page numbers and headers/footers (basic patterns)
        text = re.sub(r'Page \d+ of \d+', '', text)
        text = re.sub(r'^\d+\s*$', '', text, flags=re.MULTILINE)
        
        # Clean up common legal document artifacts
        text = re.sub(r'\[.*?\]', '', text)  # Remove bracketed references
        text = re.sub(r'\(.*?\)', '', text)  # Remove parenthetical references
        
        # Limit text length to avoid token limits
        max_chars = settings.MAX_TOKENS * 4  # Rough character to token ratio
        if len(text) > max_chars:
            text = text[:max_chars] + "..."
            logger.warning(f"Text truncated to {max_chars} characters due to length")
        
        return text.strip()
    
    def _create_simplification_prompt(
        self, 
        text: str, 
        simplification_level: str, 
        target_audience: str
    ) -> str:
        """Create a tailored prompt for document simplification."""
        
        base_prompt = settings.SIMPLIFICATION_PROMPT
        
        # Add level-specific instructions
        level_instructions = {
            "basic": """
            Provide a very simple, high-level summary suitable for someone with no legal background.
            Focus only on the most important points and use everyday language.
            Keep explanations brief and avoid legal terminology.
            """,
            "standard": """
            Provide a comprehensive but accessible explanation suitable for the general public.
            Explain key legal concepts in plain language while maintaining accuracy.
            Include important details and context.
            """,
            "detailed": """
            Provide a thorough analysis with detailed explanations of legal concepts.
            Include specific clauses, terms, and their implications.
            Suitable for someone who wants to understand the document in depth.
            """
        }
        
        # Add audience-specific instructions
        audience_instructions = {
            "general_public": "Use everyday language that anyone can understand. Avoid jargon and explain all legal terms.",
            "business_owners": "Focus on business implications, risks, and opportunities. Use business-friendly language.",
            "individuals": "Focus on personal rights, obligations, and practical implications for individuals.",
            "students": "Provide educational context and explain legal concepts with examples."
        }
        
        # Construct the full prompt
        prompt = f"""
        {base_prompt}
        
        SIMPLIFICATION LEVEL: {simplification_level.upper()}
        {level_instructions.get(simplification_level, level_instructions["standard"])}
        
        TARGET AUDIENCE: {target_audience.replace('_', ' ').title()}
        {audience_instructions.get(target_audience, audience_instructions["general_public"])}
        
        Please structure your response as a JSON object with the following fields:
        {{
            "summary": "A clear, concise summary of the document's main purpose and key points",
            "key_points": ["List of the most important points in bullet format"],
            "important_terms": {{"term": "definition", "term2": "definition2"}},
            "deadlines_obligations": ["List of any deadlines, obligations, or time-sensitive items"],
            "warnings": ["List of warnings, risks, or critical information"],
            "next_steps": ["List of recommended next steps for the reader"]
        }}
        
        DOCUMENT TO SIMPLIFY:
        {text}
        """
        
        return prompt
    
    async def _generate_simplified_content(self, prompt: str) -> str:
        """Generate simplified content using the Gemini model."""
        try:
            # Generate content with the model
            response = await asyncio.get_event_loop().run_in_executor(
                None, 
                lambda: self.model.generate_content(
                    prompt,
                    generation_config=genai.types.GenerationConfig(
                        max_output_tokens=settings.MAX_TOKENS,
                        temperature=settings.TEMPERATURE,
                    )
                )
            )
            
            if response.text:
                return response.text
            else:
                logger.error("No response text generated from Gemini model")
                raise Exception("Failed to generate simplified content")
                
        except Exception as e:
            logger.error(f"Error generating content with Gemini: {e}")
            raise
    
    def _parse_ai_response(self, response_text: str) -> Dict[str, Any]:
        """Parse the AI response and extract structured content."""
        try:
            # Try to extract JSON from the response
            json_match = re.search(r'\{.*\}', response_text, re.DOTALL)
            if json_match:
                json_str = json_match.group()
                parsed_content = json.loads(json_str)
                
                # Validate and clean the parsed content
                return self._validate_and_clean_content(parsed_content)
            else:
                # If no JSON found, try to parse the text structure
                return self._parse_text_response(response_text)
                
        except json.JSONDecodeError as e:
            logger.warning(f"Failed to parse JSON response: {e}")
            return self._parse_text_response(response_text)
        except Exception as e:
            logger.error(f"Error parsing AI response: {e}")
            return self._create_fallback_response(response_text)
    
    def _validate_and_clean_content(self, content: Dict[str, Any]) -> Dict[str, Any]:
        """Validate and clean the parsed content."""
        # Ensure all required fields exist
        required_fields = {
            "summary": "",
            "key_points": [],
            "important_terms": {},
            "deadlines_obligations": [],
            "warnings": [],
            "next_steps": []
        }
        
        for field, default_value in required_fields.items():
            if field not in content:
                content[field] = default_value
            elif field == "key_points" and not isinstance(content[field], list):
                content[field] = [str(content[field])]
            elif field == "important_terms" and not isinstance(content[field], dict):
                content[field] = {}
            elif field in ["deadlines_obligations", "warnings", "next_steps"] and not isinstance(content[field], list):
                content[field] = [str(content[field])] if content[field] else []
        
        # Clean and validate content
        content["summary"] = str(content["summary"]).strip()
        content["key_points"] = [str(point).strip() for point in content["key_points"] if str(point).strip()]
        content["deadlines_obligations"] = [str(item).strip() for item in content["deadlines_obligations"] if str(item).strip()]
        content["warnings"] = [str(warning).strip() for warning in content["warnings"] if str(warning).strip()]
        content["next_steps"] = [str(step).strip() for step in content["next_steps"] if str(step).strip()]
        
        # Clean important terms
        cleaned_terms = {}
        for term, definition in content["important_terms"].items():
            if term and definition:
                cleaned_terms[str(term).strip()] = str(definition).strip()
        content["important_terms"] = cleaned_terms
        
        return content
    
    def _parse_text_response(self, response_text: str) -> Dict[str, Any]:
        """Parse a text response when JSON parsing fails."""
        # This is a fallback method to extract information from unstructured text
        lines = response_text.split('\n')
        
        content = {
            "summary": "",
            "key_points": [],
            "important_terms": {},
            "deadlines_obligations": [],
            "warnings": [],
            "next_steps": []
        }
        
        current_section = None
        
        for line in lines:
            line = line.strip()
            if not line:
                continue
            
            # Detect sections
            if "summary" in line.lower():
                current_section = "summary"
            elif "key points" in line.lower() or "main points" in line.lower():
                current_section = "key_points"
            elif "terms" in line.lower() or "definitions" in line.lower():
                current_section = "important_terms"
            elif "deadline" in line.lower() or "obligation" in line.lower():
                current_section = "deadlines_obligations"
            elif "warning" in line.lower() or "risk" in line.lower():
                current_section = "warnings"
            elif "next step" in line.lower() or "action" in line.lower():
                current_section = "next_steps"
            elif line.startswith('-') or line.startswith('•') or line.startswith('*'):
                # Bullet point
                if current_section and current_section != "important_terms":
                    content[current_section].append(line[1:].strip())
            elif current_section == "summary" and not content["summary"]:
                content["summary"] = line
            elif current_section == "important_terms" and ':' in line:
                # Term definition
                parts = line.split(':', 1)
                if len(parts) == 2:
                    content["important_terms"][parts[0].strip()] = parts[1].strip()
        
        return content
    
    def _create_fallback_response(self, response_text: str) -> Dict[str, Any]:
        """Create a fallback response when parsing fails."""
        return {
            "summary": response_text[:500] + "..." if len(response_text) > 500 else response_text,
            "key_points": ["Unable to parse structured response"],
            "important_terms": {},
            "deadlines_obligations": [],
            "warnings": ["Please review the original document for important details"],
            "next_steps": ["Consider consulting with a legal professional"]
        }
    
    def _calculate_confidence_score(self, original_text: str, simplified_content: Dict[str, Any]) -> float:
        """Calculate a confidence score for the simplification."""
        try:
            # Simple heuristic-based confidence scoring
            score = 0.5  # Base score
            
            # Check if we have a good summary
            if simplified_content.get("summary") and len(simplified_content["summary"]) > 50:
                score += 0.2
            
            # Check if we have key points
            if simplified_content.get("key_points") and len(simplified_content["key_points"]) > 0:
                score += 0.1
            
            # Check if we have important terms
            if simplified_content.get("important_terms") and len(simplified_content["important_terms"]) > 0:
                score += 0.1
            
            # Check if we have next steps
            if simplified_content.get("next_steps") and len(simplified_content["next_steps"]) > 0:
                score += 0.1
            
            return min(score, 1.0)
            
        except Exception as e:
            logger.error(f"Error calculating confidence score: {e}")
            return 0.5
    
    def _estimate_reading_level(self, text: str) -> str:
        """Estimate the reading level of the simplified text."""
        try:
            # Simple reading level estimation based on sentence length and word complexity
            sentences = re.split(r'[.!?]+', text)
            words = text.split()
            
            if not sentences or not words:
                return "unknown"
            
            avg_sentence_length = len(words) / len(sentences)
            avg_word_length = sum(len(word) for word in words) / len(words)
            
            # Simple scoring system
            if avg_sentence_length < 10 and avg_word_length < 5:
                return "elementary"
            elif avg_sentence_length < 15 and avg_word_length < 6:
                return "intermediate"
            elif avg_sentence_length < 20 and avg_word_length < 7:
                return "high_school"
            else:
                return "college"
                
        except Exception as e:
            logger.error(f"Error estimating reading level: {e}")
            return "unknown"
    
    async def analyze_document_complexity(self, text: str) -> Dict[str, Any]:
        """Analyze the complexity of a legal document."""
        try:
            # Count legal terms and complex sentences
            legal_terms = self._count_legal_terms(text)
            complex_sentences = self._count_complex_sentences(text)
            
            # Calculate complexity metrics
            total_words = len(text.split())
            legal_term_ratio = legal_terms / total_words if total_words > 0 else 0
            complex_sentence_ratio = complex_sentences / len(re.split(r'[.!?]+', text)) if text else 0
            
            # Determine complexity level
            if legal_term_ratio > 0.1 or complex_sentence_ratio > 0.3:
                complexity_level = "high"
            elif legal_term_ratio > 0.05 or complex_sentence_ratio > 0.15:
                complexity_level = "medium"
            else:
                complexity_level = "low"
            
            return {
                "complexity_level": complexity_level,
                "legal_term_count": legal_terms,
                "legal_term_ratio": legal_term_ratio,
                "complex_sentence_count": complex_sentences,
                "complex_sentence_ratio": complex_sentence_ratio,
                "total_words": total_words,
                "estimated_reading_time": self._estimate_reading_time(total_words)
            }
            
        except Exception as e:
            logger.error(f"Error analyzing document complexity: {e}")
            return {"complexity_level": "unknown"}
    
    def _count_legal_terms(self, text: str) -> int:
        """Count legal terms in the text."""
        legal_terms = [
            "whereas", "hereby", "herein", "hereof", "hereto", "hereunder",
            "pursuant", "notwithstanding", "aforesaid", "aforementioned",
            "indemnify", "indemnification", "liability", "obligation",
            "covenant", "warrant", "represent", "guarantee", "undertake",
            "breach", "default", "termination", "rescission", "remedy",
            "damages", "penalty", "liquidated", "consequential", "incidental"
        ]
        
        text_lower = text.lower()
        count = 0
        for term in legal_terms:
            count += text_lower.count(term)
        
        return count
    
    def _count_complex_sentences(self, text: str) -> int:
        """Count complex sentences (long sentences with multiple clauses)."""
        sentences = re.split(r'[.!?]+', text)
        complex_count = 0
        
        for sentence in sentences:
            sentence = sentence.strip()
            if len(sentence.split()) > 25:  # Long sentences
                complex_count += 1
            elif sentence.count(',') > 3:  # Multiple clauses
                complex_count += 1
        
        return complex_count
    
    def _estimate_reading_time(self, word_count: int) -> int:
        """Estimate reading time in minutes (assuming 200 words per minute)."""
        return max(1, word_count // 200)

    async def answer_question(self, document_text: str, question: str, target_audience: str = "general_public") -> Dict[str, Any]:
        """Answer a question about the provided document text in simple terms."""
        try:
            cleaned_text = self._preprocess_text(document_text)
            prompt = f"""
            You are a helpful legal assistant. Answer the question based on the document content.

            TARGET AUDIENCE: {target_audience.replace('_', ' ').title()}
            Use plain, simple language. Keep the answer concise but accurate. If the answer is not explicitly in the document, say so.

            DOCUMENT:
            {cleaned_text}

            QUESTION:
            {question}

            Provide the final answer only.
            """

            response_text = await self._generate_simplified_content(prompt)
            answer_text = response_text.strip()
            # Heuristic confidence
            confidence = 0.7 if len(answer_text) > 0 else 0.3
            return {"answer": answer_text, "confidence_score": confidence}
        except Exception as e:
            logger.error(f"Error answering question: {e}")
            return {"answer": "I'm sorry, I couldn't find the answer in the document.", "confidence_score": 0.3}
