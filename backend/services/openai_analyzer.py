"""OpenAI Transaction Analysis Service - AI-powered transaction categorization."""
from typing import Optional, List, Dict, Any
import json
import httpx
from pydantic import BaseModel


class TransactionAnalysis(BaseModel):
    """AI analysis result for a transaction"""
    suggested_category: Optional[str] = None
    transaction_type: str = "expense"  # "income" or "expense"
    is_recurring: bool = False
    recurring_frequency: Optional[str] = None  # "monthly", "weekly", "yearly", etc.
    is_unusual: bool = False
    unusual_reason: Optional[str] = None
    confidence: float = 0.0


class OpenAITransactionAnalyzer:
    """Analyzes transactions using OpenAI API"""
    
    AVAILABLE_MODELS = [
        "gpt-4o-mini",
        "gpt-4o",
        "gpt-4-turbo",
        "gpt-3.5-turbo"
    ]
    
    DEFAULT_CATEGORIES = [
        "Food & Dining",
        "Groceries",
        "Transportation",
        "Utilities",
        "Housing",
        "Healthcare",
        "Entertainment",
        "Shopping",
        "Travel",
        "Education",
        "Insurance",
        "Subscriptions",
        "Personal Care",
        "Gifts & Donations",
        "Business",
        "Investments",
        "Salary",
        "Freelance Income",
        "Rental Income",
        "Interest & Dividends",
        "Refunds",
        "Other Income",
        "Other Expense"
    ]
    
    def __init__(self, api_key: str, model: str = "gpt-4o-mini"):
        self.api_key = api_key
        self.model = model if model in self.AVAILABLE_MODELS else "gpt-4o-mini"
        self.base_url = "https://api.openai.com/v1/chat/completions"
    
    async def analyze_transactions(
        self, 
        transactions: List[Dict[str, Any]],
        existing_categories: Optional[List[str]] = None,
        historical_transactions: Optional[List[Dict[str, Any]]] = None
    ) -> List[TransactionAnalysis]:
        """
        Analyze a batch of transactions using AI.
        
        Args:
            transactions: List of transaction dicts with date, amount, description
            existing_categories: User's existing categories to match against
            historical_transactions: Recent transactions to compare for patterns
        """
        if not transactions:
            return []
        
        # Use provided categories or defaults
        categories = existing_categories if existing_categories else self.DEFAULT_CATEGORIES
        
        # Build the prompt
        system_prompt = self._build_system_prompt(categories)
        user_prompt = self._build_user_prompt(transactions, historical_transactions)
        
        try:
            async with httpx.AsyncClient(timeout=60.0) as client:
                response = await client.post(
                    self.base_url,
                    headers={
                        "Authorization": f"Bearer {self.api_key}",
                        "Content-Type": "application/json"
                    },
                    json={
                        "model": self.model,
                        "messages": [
                            {"role": "system", "content": system_prompt},
                            {"role": "user", "content": user_prompt}
                        ],
                        "temperature": 0.3,
                        "response_format": {"type": "json_object"}
                    }
                )
                
                if response.status_code == 401:
                    raise ValueError("Invalid OpenAI API key")
                elif response.status_code == 429:
                    raise ValueError("OpenAI API rate limit exceeded. Please try again later.")
                elif response.status_code != 200:
                    raise ValueError(f"OpenAI API error: {response.status_code}")
                
                result = response.json()
                content = result["choices"][0]["message"]["content"]
                
                return self._parse_response(content, len(transactions))
                
        except httpx.TimeoutException:
            raise ValueError("OpenAI API request timed out. Please try again.")
        except json.JSONDecodeError:
            raise ValueError("Failed to parse OpenAI response")
        except Exception as e:
            if "Invalid OpenAI API key" in str(e) or "rate limit" in str(e).lower():
                raise
            raise ValueError(f"AI analysis failed: {str(e)}")
    
    def _build_system_prompt(self, categories: List[str]) -> str:
        return f"""You are a financial transaction analyzer. Analyze bank transactions and provide:
1. Category suggestion from this list: {', '.join(categories)}
2. Whether it's income or expense
3. Whether it appears to be recurring (subscription, regular payment, salary, etc.)
4. Whether the amount seems unusual (significantly higher/lower than typical)

For recurring detection, look for patterns like:
- Subscription services (Netflix, Spotify, etc.)
- Utility bills (electricity, water, internet)
- Insurance payments
- Salary/regular income
- Loan/mortgage payments
- Memberships

For unusual detection, flag transactions that:
- Have unusually high amounts for the category
- Appear to be one-time large purchases
- Have amounts significantly different from similar past transactions

Respond in JSON format with an array called "analyses" containing objects with:
- suggested_category: string (from provided categories)
- transaction_type: "income" or "expense"
- is_recurring: boolean
- recurring_frequency: "daily", "weekly", "monthly", "yearly", or null
- is_unusual: boolean
- unusual_reason: string or null (brief explanation if unusual)
- confidence: number 0-1 (how confident in the categorization)"""

    def _build_user_prompt(
        self, 
        transactions: List[Dict[str, Any]], 
        historical: Optional[List[Dict[str, Any]]] = None
    ) -> str:
        # Format transactions for analysis
        tx_list = []
        for i, tx in enumerate(transactions):
            tx_str = f"{i+1}. Date: {tx.get('date', 'N/A')}, Amount: {tx.get('amount', 0):.2f}"
            if tx.get('description'):
                tx_str += f", Description: {tx['description']}"
            if tx.get('payee'):
                tx_str += f", Payee: {tx['payee']}"
            if tx.get('memo'):
                tx_str += f", Memo: {tx['memo']}"
            tx_list.append(tx_str)
        
        prompt = f"Analyze these {len(transactions)} transactions:\n\n" + "\n".join(tx_list)
        
        # Add historical context if available
        if historical and len(historical) > 0:
            hist_summary = []
            for h in historical[:20]:  # Limit to recent 20
                hist_summary.append(f"- {h.get('date', 'N/A')}: {h.get('amount', 0):.2f} - {h.get('description', 'N/A')}")
            prompt += f"\n\nRecent transaction history for context:\n" + "\n".join(hist_summary)
        
        return prompt
    
    def _parse_response(self, content: str, expected_count: int) -> List[TransactionAnalysis]:
        """Parse the OpenAI response into TransactionAnalysis objects"""
        try:
            data = json.loads(content)
            analyses = data.get("analyses", [])
            
            results = []
            for i, analysis in enumerate(analyses):
                if i >= expected_count:
                    break
                results.append(TransactionAnalysis(
                    suggested_category=analysis.get("suggested_category"),
                    transaction_type=analysis.get("transaction_type", "expense"),
                    is_recurring=analysis.get("is_recurring", False),
                    recurring_frequency=analysis.get("recurring_frequency"),
                    is_unusual=analysis.get("is_unusual", False),
                    unusual_reason=analysis.get("unusual_reason"),
                    confidence=analysis.get("confidence", 0.5)
                ))
            
            # Fill missing with defaults
            while len(results) < expected_count:
                results.append(TransactionAnalysis())
            
            return results
            
        except json.JSONDecodeError:
            # Return defaults if parsing fails
            return [TransactionAnalysis() for _ in range(expected_count)]


async def test_openai_connection(api_key: str, model: str = "gpt-4o-mini") -> Dict[str, Any]:
    """Test if the OpenAI API key is valid"""
    try:
        async with httpx.AsyncClient(timeout=10.0) as client:
            response = await client.post(
                "https://api.openai.com/v1/chat/completions",
                headers={
                    "Authorization": f"Bearer {api_key}",
                    "Content-Type": "application/json"
                },
                json={
                    "model": model,
                    "messages": [{"role": "user", "content": "Say 'OK'"}],
                    "max_tokens": 5
                }
            )
            
            if response.status_code == 200:
                return {"valid": True, "message": "API key is valid"}
            elif response.status_code == 401:
                return {"valid": False, "message": "Invalid API key"}
            elif response.status_code == 429:
                return {"valid": True, "message": "API key valid but rate limited"}
            else:
                return {"valid": False, "message": f"API error: {response.status_code}"}
                
    except Exception as e:
        return {"valid": False, "message": f"Connection failed: {str(e)}"}
