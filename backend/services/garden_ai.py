"""Garden Designer AI Service - AI-powered garden layout generation."""
from typing import Optional, List, Dict, Any
import json
import httpx
from pydantic import BaseModel


class PlantPlacement(BaseModel):
    """A single plant placement in the garden"""
    name: str
    category: str  # vegetable, herb, fruit_tree, etc.
    x: float  # Position in meters from origin
    y: float  # Position in meters from origin
    radius: float  # Space needed (meters)
    sun_requirement: str  # "full_sun", "partial_shade", "shade"
    water_need: str  # "low", "medium", "high"
    height: str  # "ground_cover", "low", "medium", "tall", "tree"
    notes: str  # Planting tips


class GardenZone(BaseModel):
    """A zone in the garden with specific characteristics"""
    name: str
    type: str  # "sun", "partial_shade", "shade", "windbreak", "water"
    points: List[Dict[str, float]]  # Polygon points defining the zone
    description: str


class GardenDesignResult(BaseModel):
    """Complete AI-generated garden design"""
    plants: List[PlantPlacement]
    zones: List[GardenZone]
    sun_analysis: str
    wind_analysis: str
    climate_info: str
    design_summary: str
    planting_tips: List[str]
    seasonal_tasks: Dict[str, List[str]]


class GardenDesignerAI:
    """Generates garden designs using OpenAI API"""
    
    def __init__(self, api_key: str, model: str = "gpt-4o-mini"):
        self.api_key = api_key
        self.model = model
        self.base_url = "https://api.openai.com/v1/chat/completions"
    
    async def generate_design(
        self,
        boundary_points: List[Dict[str, float]],
        scale: float,  # meters per grid unit
        latitude: float,
        longitude: float,
        wind_direction: str,
        garden_goal: str,
        plant_preferences: List[str],
        custom_plants: Optional[str] = None,
        existing_features: Optional[List[str]] = None,
        custom_features: Optional[str] = None,
        notes: Optional[str] = None
    ) -> GardenDesignResult:
        """
        Generate a complete garden design based on user inputs.
        """
        
        # Calculate garden dimensions
        xs = [p['x'] * scale for p in boundary_points]
        ys = [p['y'] * scale for p in boundary_points]
        min_x, max_x = min(xs), max(xs)
        min_y, max_y = min(ys), max(ys)
        width = max_x - min_x
        height = max_y - min_y
        
        # Calculate area using shoelace formula
        n = len(boundary_points)
        area = 0
        for i in range(n):
            j = (i + 1) % n
            area += boundary_points[i]['x'] * boundary_points[j]['y']
            area -= boundary_points[j]['x'] * boundary_points[i]['y']
        area = abs(area) / 2 * scale * scale
        
        system_prompt = self._build_system_prompt()
        user_prompt = self._build_user_prompt(
            boundary_points=boundary_points,
            scale=scale,
            width=width,
            height=height,
            area=area,
            latitude=latitude,
            longitude=longitude,
            wind_direction=wind_direction,
            garden_goal=garden_goal,
            plant_preferences=plant_preferences,
            custom_plants=custom_plants,
            existing_features=existing_features,
            custom_features=custom_features,
            notes=notes
        )
        
        try:
            async with httpx.AsyncClient(timeout=120.0) as client:
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
                        "temperature": 0.7,
                        "max_tokens": 4000,
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
                
                return self._parse_response(content, width, height)
                
        except httpx.TimeoutException:
            raise ValueError("AI request timed out. Please try again.")
        except json.JSONDecodeError as e:
            raise ValueError(f"Failed to parse AI response: {str(e)}")
        except Exception as e:
            if "Invalid OpenAI API key" in str(e) or "rate limit" in str(e).lower():
                raise
            raise ValueError(f"Garden design generation failed: {str(e)}")
    
    def _build_system_prompt(self) -> str:
        return """You are an expert permaculture garden designer and horticulturist. You design gardens based on:
- Sun path analysis (based on latitude for sunrise/sunset angles)
- Wind protection and microclimate creation
- Companion planting principles
- Permaculture layering (canopy, understory, shrub, herbaceous, ground cover, vine, root)
- Water management and efficient irrigation zones
- Seasonal considerations

When placing plants, consider:
1. Sun requirements - place sun-loving plants where they get 6+ hours direct sun
2. Wind protection - use taller plants/trees as windbreaks on the windward side
3. Height layering - taller plants to the north (in northern hemisphere) to avoid shading
4. Companion planting - place beneficial companions together
5. Access paths - leave space for harvesting and maintenance
6. Water zones - group plants with similar water needs

You must respond with a JSON object containing:
{
  "plants": [
    {
      "name": "Plant name",
      "category": "vegetable|herb|fruit_tree|berry|nut_tree|leafy|legume|root|flower|medicinal",
      "x": <number in meters from left edge>,
      "y": <number in meters from top edge>,
      "radius": <space needed in meters>,
      "sun_requirement": "full_sun|partial_shade|shade",
      "water_need": "low|medium|high",
      "height": "ground_cover|low|medium|tall|tree",
      "notes": "Brief planting tip"
    }
  ],
  "zones": [
    {
      "name": "Zone name",
      "type": "sun|partial_shade|shade|windbreak|water",
      "points": [{"x": 0, "y": 0}, ...],
      "description": "Zone description"
    }
  ],
  "sun_analysis": "Description of sun patterns for this location",
  "wind_analysis": "How wind affects the garden and mitigation strategies",
  "climate_info": "Climate zone and growing season information",
  "design_summary": "Overview of the garden design approach",
  "planting_tips": ["Tip 1", "Tip 2", ...],
  "seasonal_tasks": {
    "spring": ["Task 1", ...],
    "summer": ["Task 1", ...],
    "autumn": ["Task 1", ...],
    "winter": ["Task 1", ...]
  }
}

Place plants WITHIN the garden boundary. Coordinates should be in meters from the top-left corner of the bounding box."""

    def _build_user_prompt(
        self,
        boundary_points: List[Dict[str, float]],
        scale: float,
        width: float,
        height: float,
        area: float,
        latitude: float,
        longitude: float,
        wind_direction: str,
        garden_goal: str,
        plant_preferences: List[str],
        custom_plants: Optional[str],
        existing_features: Optional[List[str]],
        custom_features: Optional[str],
        notes: Optional[str]
    ) -> str:
        # Convert boundary to meters for the prompt
        boundary_meters = [{"x": p['x'] * scale, "y": p['y'] * scale} for p in boundary_points]
        
        # Map garden goal to description
        goal_descriptions = {
            "simple": "Simple kitchen garden with basic herbs and vegetables for daily cooking",
            "mixed": "Mixed garden with combination of vegetables, herbs, and some fruit",
            "forest": "Full food forest with multiple layers - trees, shrubs, and ground cover",
            "permaculture": "Complete permaculture design with self-sustaining ecosystem"
        }
        
        # Map plant preferences to full names
        plant_category_names = {
            "vegetables": "Vegetables (tomatoes, peppers, carrots, etc.)",
            "herbs": "Culinary and aromatic herbs",
            "fruits": "Fruit trees",
            "berries": "Berry bushes and plants",
            "nuts": "Nut trees",
            "leafy": "Leafy greens (lettuce, spinach, kale)",
            "legumes": "Legumes (beans, peas)",
            "root": "Root vegetables (potatoes, beets, onions)",
            "flowers": "Edible flowers",
            "medicinal": "Medicinal plants"
        }
        
        prompt = f"""Design a garden with the following specifications:

## Garden Shape & Size
- Boundary points (in meters): {json.dumps(boundary_meters)}
- Approximate dimensions: {width:.1f}m wide × {height:.1f}m tall
- Total area: {area:.1f} m²
- Shape: {'Triangle' if len(boundary_points) == 3 else 'Rectangle' if len(boundary_points) == 4 else 'Polygon'} with {len(boundary_points)} vertices

## Location & Climate
- GPS Coordinates: {latitude}° latitude, {longitude}° longitude
- Hemisphere: {'Northern' if latitude >= 0 else 'Southern'}
- Based on latitude, determine approximate climate zone and growing season

## Environmental Factors
- Prevailing wind direction: From the {wind_direction}
- Place windbreaks/taller plants on the {wind_direction} side to protect the garden

## Garden Type
{goal_descriptions.get(garden_goal, garden_goal)}

## Desired Plants
Categories requested: {', '.join(plant_category_names.get(p, p) for p in plant_preferences)}
"""
        
        if custom_plants:
            prompt += f"\nSpecific plants requested: {custom_plants}"
        
        if existing_features:
            feature_names = {
                "house": "House/Building (consider shade it casts)",
                "shed": "Shed/Outbuilding",
                "trees": "Existing mature trees",
                "pond": "Pond or water feature",
                "slope": "Sloped terrain",
                "fence": "Fence or wall"
            }
            prompt += f"\n\n## Existing Features\n{', '.join(feature_names.get(f, f) for f in existing_features)}"
        
        if custom_features:
            prompt += f"\nOther features: {custom_features}"
        
        if notes:
            prompt += f"\n\n## Additional Notes\n{notes}"
        
        prompt += """

## Design Requirements
1. Place all plants WITHIN the boundary polygon
2. Use coordinates in meters from the top-left of the bounding box
3. Consider sun path based on latitude (sun rises in east, sets in west, higher in south for northern hemisphere)
4. Create distinct zones for different sun/shade conditions
5. Include at least 10-20 plants appropriate for the garden size
6. Ensure proper spacing between plants
7. Group companion plants together
8. Leave paths for access (don't fill every space)

Generate a complete garden design JSON response."""
        
        return prompt
    
    def _parse_response(self, content: str, width: float, height: float) -> GardenDesignResult:
        """Parse the AI response into structured data"""
        try:
            data = json.loads(content)
            
            # Parse plants
            plants = []
            for p in data.get("plants", []):
                # Ensure plants are within bounds
                x = max(0, min(float(p.get("x", 0)), width))
                y = max(0, min(float(p.get("y", 0)), height))
                
                plants.append(PlantPlacement(
                    name=p.get("name", "Unknown"),
                    category=p.get("category", "vegetable"),
                    x=x,
                    y=y,
                    radius=float(p.get("radius", 0.5)),
                    sun_requirement=p.get("sun_requirement", "full_sun"),
                    water_need=p.get("water_need", "medium"),
                    height=p.get("height", "medium"),
                    notes=p.get("notes", "")
                ))
            
            # Parse zones
            zones = []
            for z in data.get("zones", []):
                zones.append(GardenZone(
                    name=z.get("name", "Zone"),
                    type=z.get("type", "sun"),
                    points=z.get("points", []),
                    description=z.get("description", "")
                ))
            
            return GardenDesignResult(
                plants=plants,
                zones=zones,
                sun_analysis=data.get("sun_analysis", ""),
                wind_analysis=data.get("wind_analysis", ""),
                climate_info=data.get("climate_info", ""),
                design_summary=data.get("design_summary", ""),
                planting_tips=data.get("planting_tips", []),
                seasonal_tasks=data.get("seasonal_tasks", {})
            )
            
        except (json.JSONDecodeError, KeyError) as e:
            raise ValueError(f"Failed to parse garden design: {str(e)}")
