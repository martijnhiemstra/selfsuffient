import { useState, useRef, useEffect, useCallback } from 'react';
import { useParams, useNavigate } from 'react-router-dom';
import { Stage, Layer, Line, Circle, Rect, Text, Group } from 'react-konva';
import { useAuth } from '../context/AuthContext';
import { Card, CardContent, CardHeader, CardTitle, CardDescription } from '../components/ui/card';
import { Button } from '../components/ui/button';
import { Input } from '../components/ui/input';
import { Label } from '../components/ui/label';
import { Slider } from '../components/ui/slider';
import { Textarea } from '../components/ui/textarea';
import { Tabs, TabsContent, TabsList, TabsTrigger } from '../components/ui/tabs';
import { Badge } from '../components/ui/badge';
import {
  Select,
  SelectContent,
  SelectItem,
  SelectTrigger,
  SelectValue,
} from '../components/ui/select';
import { 
  ArrowLeft, 
  Trash2, 
  RotateCcw, 
  Save,
  Grid3X3,
  Maximize2,
  MousePointer2,
  Pencil,
  Move,
  Info,
  MapPin,
  Wind,
  Target,
  Leaf,
  TreeDeciduous,
  Home,
  Sun,
  Compass,
  Sparkles,
  ChevronRight,
  X
} from 'lucide-react';
import { toast } from 'sonner';
import axios from 'axios';

const API = `${process.env.REACT_APP_BACKEND_URL}/api`;

// Calculate area of a polygon using Shoelace formula
const calculatePolygonArea = (points, scale) => {
  if (points.length < 3) return 0;
  
  let area = 0;
  const n = points.length;
  
  for (let i = 0; i < n; i++) {
    const j = (i + 1) % n;
    area += points[i].x * points[j].y;
    area -= points[j].x * points[i].y;
  }
  
  area = Math.abs(area) / 2;
  // Convert from grid squares to square meters
  return area * scale * scale;
};

// Calculate perimeter
const calculatePerimeter = (points, scale) => {
  if (points.length < 2) return 0;
  
  let perimeter = 0;
  for (let i = 0; i < points.length; i++) {
    const j = (i + 1) % points.length;
    const dx = points[j].x - points[i].x;
    const dy = points[j].y - points[i].y;
    perimeter += Math.sqrt(dx * dx + dy * dy);
  }
  
  return perimeter * scale;
};

// Calculate bounding box dimensions
const calculateBoundingBox = (points, scale) => {
  if (points.length === 0) return { width: 0, height: 0 };
  
  const xs = points.map(p => p.x);
  const ys = points.map(p => p.y);
  
  const minX = Math.min(...xs);
  const maxX = Math.max(...xs);
  const minY = Math.min(...ys);
  const maxY = Math.max(...ys);
  
  return {
    width: (maxX - minX) * scale,
    height: (maxY - minY) * scale
  };
};

export const GardenDesignerPage = () => {
  const { projectId } = useParams();
  const navigate = useNavigate();
  const { token } = useAuth();
  const stageRef = useRef(null);
  const containerRef = useRef(null);

  // Project info
  const [project, setProject] = useState(null);
  const [loading, setLoading] = useState(true);

  // Current step/tab
  const [activeTab, setActiveTab] = useState('draw'); // 'draw', 'details', 'generate'

  // Canvas state
  const [stageSize, setStageSize] = useState({ width: 800, height: 600 });
  const [points, setPoints] = useState([]);
  const [isDrawing, setIsDrawing] = useState(true);
  const [selectedPointIndex, setSelectedPointIndex] = useState(null);
  const [isClosed, setIsClosed] = useState(false);

  // Grid settings
  const [gridScale, setGridScale] = useState(1); // meters per grid square
  const [gridSize, setGridSize] = useState(40); // pixels per grid square
  const [showGrid, setShowGrid] = useState(true);

  // Tool mode
  const [tool, setTool] = useState('draw'); // 'draw', 'select', 'move'

  // Garden Details Form State (Phase 2)
  const [gardenDetails, setGardenDetails] = useState({
    // Location
    latitude: '',
    longitude: '',
    // Wind
    windDirection: '',
    // Garden type/goal
    gardenGoal: '',
    // Plant preferences
    plantPreferences: [],
    customPlants: '',
    // Existing features
    existingFeatures: [],
    customFeatures: '',
    // Additional notes
    notes: ''
  });

  // Predefined plant options
  const plantOptions = [
    { id: 'vegetables', label: 'Vegetables', examples: 'tomatoes, peppers, carrots' },
    { id: 'herbs', label: 'Herbs', examples: 'basil, rosemary, thyme' },
    { id: 'fruits', label: 'Fruit trees', examples: 'apple, pear, cherry' },
    { id: 'berries', label: 'Berries', examples: 'strawberries, blueberries, raspberries' },
    { id: 'nuts', label: 'Nut trees', examples: 'walnut, hazelnut, almond' },
    { id: 'leafy', label: 'Leafy greens', examples: 'lettuce, spinach, kale' },
    { id: 'legumes', label: 'Legumes', examples: 'beans, peas, lentils' },
    { id: 'root', label: 'Root vegetables', examples: 'potatoes, beets, onions' },
    { id: 'flowers', label: 'Edible flowers', examples: 'nasturtium, calendula, lavender' },
    { id: 'medicinal', label: 'Medicinal plants', examples: 'echinacea, chamomile, mint' },
  ];

  // Predefined existing feature options
  const featureOptions = [
    { id: 'house', label: 'House/Building', icon: Home },
    { id: 'shed', label: 'Shed/Outbuilding', icon: Home },
    { id: 'trees', label: 'Existing trees', icon: TreeDeciduous },
    { id: 'pond', label: 'Pond/Water feature', icon: Leaf },
    { id: 'slope', label: 'Slope/Hill', icon: Compass },
    { id: 'fence', label: 'Fence/Wall', icon: Grid3X3 },
  ];

  // Wind direction options
  const windDirections = [
    { value: 'N', label: 'North', angle: 0 },
    { value: 'NE', label: 'Northeast', angle: 45 },
    { value: 'E', label: 'East', angle: 90 },
    { value: 'SE', label: 'Southeast', angle: 135 },
    { value: 'S', label: 'South', angle: 180 },
    { value: 'SW', label: 'Southwest', angle: 225 },
    { value: 'W', label: 'West', angle: 270 },
    { value: 'NW', label: 'Northwest', angle: 315 },
  ];

  // Garden goal options
  const gardenGoals = [
    { 
      value: 'simple', 
      label: 'Simple Kitchen Garden', 
      description: 'Basic herbs and vegetables for daily cooking',
      icon: Leaf
    },
    { 
      value: 'mixed', 
      label: 'Mixed Garden', 
      description: 'Combination of vegetables, herbs, and some fruit',
      icon: TreeDeciduous
    },
    { 
      value: 'forest', 
      label: 'Full Forest Garden', 
      description: 'Multi-layered food forest with trees, shrubs, and ground cover',
      icon: TreeDeciduous
    },
    { 
      value: 'permaculture', 
      label: 'Permaculture Design', 
      description: 'Self-sustaining ecosystem with companion planting',
      icon: Sparkles
    },
  ];

  const headers = { Authorization: `Bearer ${token}` };

  // Update garden details
  const updateGardenDetails = (field, value) => {
    setGardenDetails(prev => ({ ...prev, [field]: value }));
  };

  // Toggle plant preference
  const togglePlantPreference = (plantId) => {
    setGardenDetails(prev => ({
      ...prev,
      plantPreferences: prev.plantPreferences.includes(plantId)
        ? prev.plantPreferences.filter(p => p !== plantId)
        : [...prev.plantPreferences, plantId]
    }));
  };

  // Toggle existing feature
  const toggleFeature = (featureId) => {
    setGardenDetails(prev => ({
      ...prev,
      existingFeatures: prev.existingFeatures.includes(featureId)
        ? prev.existingFeatures.filter(f => f !== featureId)
        : [...prev.existingFeatures, featureId]
    }));
  };

  // Generation state
  const [isGenerating, setIsGenerating] = useState(false);
  const [generatedDesign, setGeneratedDesign] = useState(null);
  const [generationError, setGenerationError] = useState(null);

  // Generate garden design
  const handleGenerateDesign = async () => {
    setIsGenerating(true);
    setGenerationError(null);
    
    try {
      const response = await axios.post(`${API}/garden/generate`, {
        project_id: projectId,
        boundary: {
          points: points,
          scale: gridScale
        },
        details: {
          latitude: parseFloat(gardenDetails.latitude),
          longitude: parseFloat(gardenDetails.longitude),
          wind_direction: gardenDetails.windDirection,
          garden_goal: gardenDetails.gardenGoal,
          plant_preferences: gardenDetails.plantPreferences,
          custom_plants: gardenDetails.customPlants || null,
          existing_features: gardenDetails.existingFeatures.length > 0 ? gardenDetails.existingFeatures : null,
          custom_features: gardenDetails.customFeatures || null,
          notes: gardenDetails.notes || null
        }
      }, { headers });
      
      setGeneratedDesign(response.data);
      toast.success('Garden design generated successfully!');
    } catch (err) {
      const errorMsg = err.response?.data?.detail || 'Failed to generate design';
      setGenerationError(errorMsg);
      if (errorMsg.includes('API key')) {
        toast.error('Please configure your OpenAI API key in Settings first.');
      } else {
        toast.error(errorMsg);
      }
    } finally {
      setIsGenerating(false);
    }
  };

  // Check if form is valid for generation
  const isFormValid = () => {
    return (
      isClosed &&
      points.length >= 3 &&
      gardenDetails.latitude &&
      gardenDetails.longitude &&
      gardenDetails.windDirection &&
      gardenDetails.gardenGoal &&
      gardenDetails.plantPreferences.length > 0
    );
  };

  // Fetch project info
  useEffect(() => {
    const fetchProject = async () => {
      try {
        const res = await axios.get(`${API}/projects/${projectId}`, { headers });
        setProject(res.data);
      } catch (err) {
        toast.error('Failed to load project');
        navigate('/projects');
      } finally {
        setLoading(false);
      }
    };
    fetchProject();
  }, [projectId]);

  // Resize canvas to fit container
  useEffect(() => {
    const updateSize = () => {
      if (containerRef.current) {
        const rect = containerRef.current.getBoundingClientRect();
        setStageSize({
          width: rect.width,
          height: Math.max(500, window.innerHeight - 300)
        });
      }
    };

    updateSize();
    window.addEventListener('resize', updateSize);
    return () => window.removeEventListener('resize', updateSize);
  }, []);

  // Handle canvas click
  const handleStageClick = (e) => {
    if (tool !== 'draw' || isClosed) return;

    const stage = e.target.getStage();
    const pos = stage.getPointerPosition();
    
    // Snap to grid
    const snappedX = Math.round(pos.x / gridSize) * gridSize;
    const snappedY = Math.round(pos.y / gridSize) * gridSize;

    // Check if clicking near the first point to close the polygon
    if (points.length >= 3) {
      const firstPoint = points[0];
      const distance = Math.sqrt(
        Math.pow(snappedX - firstPoint.x * gridSize, 2) + 
        Math.pow(snappedY - firstPoint.y * gridSize, 2)
      );
      
      if (distance < 30) {  // Increased detection radius
        setIsClosed(true);
        setIsDrawing(false);
        setTool('select');
        toast.success('Garden boundary completed!');
        return;
      }
    }

    // Add new point (store in grid units, not pixels)
    const newPoint = { 
      x: snappedX / gridSize, 
      y: snappedY / gridSize 
    };
    setPoints([...points, newPoint]);
  };

  // Handle point drag
  const handlePointDrag = (index, e) => {
    const newPoints = [...points];
    newPoints[index] = {
      x: Math.round(e.target.x() / gridSize),
      y: Math.round(e.target.y() / gridSize)
    };
    setPoints(newPoints);
  };

  // Clear all points
  const handleClear = () => {
    setPoints([]);
    setIsClosed(false);
    setIsDrawing(true);
    setTool('draw');
    setSelectedPointIndex(null);
  };

  // Remove last point
  const handleUndo = () => {
    if (points.length > 0) {
      setPoints(points.slice(0, -1));
      if (isClosed) {
        setIsClosed(false);
        setIsDrawing(true);
        setTool('draw');
      }
    }
  };

  // Delete selected point
  const handleDeletePoint = () => {
    if (selectedPointIndex !== null && points.length > 3) {
      const newPoints = points.filter((_, i) => i !== selectedPointIndex);
      setPoints(newPoints);
      setSelectedPointIndex(null);
    } else if (points.length <= 3) {
      toast.error('Need at least 3 points for a shape');
    }
  };

  // Generate grid lines
  const gridLines = [];
  if (showGrid) {
    // Vertical lines
    for (let x = 0; x <= stageSize.width; x += gridSize) {
      gridLines.push(
        <Line
          key={`v-${x}`}
          points={[x, 0, x, stageSize.height]}
          stroke="#e5e7eb"
          strokeWidth={1}
        />
      );
    }
    // Horizontal lines
    for (let y = 0; y <= stageSize.height; y += gridSize) {
      gridLines.push(
        <Line
          key={`h-${y}`}
          points={[0, y, stageSize.width, y]}
          stroke="#e5e7eb"
          strokeWidth={1}
        />
      );
    }
  }

  // Convert points to flat array for Line component (in pixels)
  const linePoints = points.flatMap(p => [p.x * gridSize, p.y * gridSize]);
  if (isClosed && points.length > 0) {
    linePoints.push(points[0].x * gridSize, points[0].y * gridSize);
  }

  // Calculate measurements
  const area = calculatePolygonArea(points, gridScale);
  const perimeter = calculatePerimeter(points, gridScale);
  const boundingBox = calculateBoundingBox(points, gridScale);

  // Scale presets
  const scalePresets = [
    { value: 0.5, label: '0.5m per square (small garden)' },
    { value: 1, label: '1m per square (medium garden)' },
    { value: 2, label: '2m per square (large garden)' },
    { value: 5, label: '5m per square (very large)' },
    { value: 10, label: '10m per square (field)' },
    { value: 25, label: '25m per square (hectare+)' },
  ];

  if (loading) {
    return (
      <div className="flex items-center justify-center h-64">
        <div className="animate-spin rounded-full h-8 w-8 border-b-2 border-primary"></div>
      </div>
    );
  }

  return (
    <div className="space-y-6" data-testid="garden-designer-page">
      {/* Header */}
      <div className="flex items-center justify-between">
        <div className="flex items-center gap-4">
          <Button 
            variant="ghost" 
            size="sm" 
            onClick={() => navigate(`/projects/${projectId}`)}
          >
            <ArrowLeft className="w-4 h-4 mr-2" />
            Back to {project?.name}
          </Button>
        </div>
        <h1 className="text-2xl font-bold">Garden Designer</h1>
      </div>

      {/* Progress Steps */}
      <div className="flex items-center justify-center gap-2">
        <div 
          className={`flex items-center gap-2 px-4 py-2 rounded-full cursor-pointer transition-all ${
            activeTab === 'draw' ? 'bg-primary text-primary-foreground' : 'bg-muted hover:bg-muted/80'
          }`}
          onClick={() => setActiveTab('draw')}
        >
          <span className="w-6 h-6 rounded-full bg-background/20 flex items-center justify-center text-sm font-medium">1</span>
          <span className="font-medium">Draw Boundary</span>
          {isClosed && <span className="text-green-400">✓</span>}
        </div>
        <ChevronRight className="w-4 h-4 text-muted-foreground" />
        <div 
          className={`flex items-center gap-2 px-4 py-2 rounded-full cursor-pointer transition-all ${
            activeTab === 'details' ? 'bg-primary text-primary-foreground' : 'bg-muted hover:bg-muted/80'
          } ${!isClosed ? 'opacity-50 cursor-not-allowed' : ''}`}
          onClick={() => isClosed && setActiveTab('details')}
        >
          <span className="w-6 h-6 rounded-full bg-background/20 flex items-center justify-center text-sm font-medium">2</span>
          <span className="font-medium">Garden Details</span>
          {isFormValid() && <span className="text-green-400">✓</span>}
        </div>
        <ChevronRight className="w-4 h-4 text-muted-foreground" />
        <div 
          className={`flex items-center gap-2 px-4 py-2 rounded-full cursor-pointer transition-all ${
            activeTab === 'generate' ? 'bg-primary text-primary-foreground' : 'bg-muted hover:bg-muted/80'
          } ${!isFormValid() ? 'opacity-50 cursor-not-allowed' : ''}`}
          onClick={() => isFormValid() && setActiveTab('generate')}
        >
          <span className="w-6 h-6 rounded-full bg-background/20 flex items-center justify-center text-sm font-medium">3</span>
          <span className="font-medium">Generate Design</span>
        </div>
      </div>

      {/* Tab Content */}
      {activeTab === 'draw' && (
        <div className="grid grid-cols-1 lg:grid-cols-4 gap-6">
        {/* Tools Panel */}
        <div className="lg:col-span-1 space-y-4">
          {/* Scale Settings */}
          <Card>
            <CardHeader className="pb-3">
              <CardTitle className="text-sm flex items-center gap-2">
                <Grid3X3 className="w-4 h-4" />
                Grid Scale
              </CardTitle>
            </CardHeader>
            <CardContent className="space-y-4">
              <div className="space-y-2">
                <Label>Meters per square</Label>
                <Select 
                  value={gridScale.toString()} 
                  onValueChange={(v) => setGridScale(parseFloat(v))}
                >
                  <SelectTrigger>
                    <SelectValue />
                  </SelectTrigger>
                  <SelectContent>
                    {scalePresets.map(preset => (
                      <SelectItem key={preset.value} value={preset.value.toString()}>
                        {preset.label}
                      </SelectItem>
                    ))}
                  </SelectContent>
                </Select>
              </div>

              <div className="space-y-2">
                <Label>Grid size (display)</Label>
                <Slider
                  value={[gridSize]}
                  onValueChange={(v) => setGridSize(v[0])}
                  min={20}
                  max={80}
                  step={10}
                />
                <p className="text-xs text-muted-foreground">{gridSize}px per square</p>
              </div>

              <div className="flex items-center gap-2">
                <input
                  type="checkbox"
                  id="showGrid"
                  checked={showGrid}
                  onChange={(e) => setShowGrid(e.target.checked)}
                  className="rounded"
                />
                <Label htmlFor="showGrid" className="text-sm cursor-pointer">Show grid</Label>
              </div>
            </CardContent>
          </Card>

          {/* Drawing Tools */}
          <Card>
            <CardHeader className="pb-3">
              <CardTitle className="text-sm">Tools</CardTitle>
            </CardHeader>
            <CardContent className="space-y-2">
              <div className="grid grid-cols-3 gap-2">
                <Button
                  variant={tool === 'draw' ? 'default' : 'outline'}
                  size="sm"
                  onClick={() => setTool('draw')}
                  disabled={isClosed}
                  className="flex flex-col h-auto py-2"
                >
                  <Pencil className="w-4 h-4 mb-1" />
                  <span className="text-xs">Draw</span>
                </Button>
                <Button
                  variant={tool === 'select' ? 'default' : 'outline'}
                  size="sm"
                  onClick={() => setTool('select')}
                  className="flex flex-col h-auto py-2"
                >
                  <MousePointer2 className="w-4 h-4 mb-1" />
                  <span className="text-xs">Select</span>
                </Button>
                <Button
                  variant={tool === 'move' ? 'default' : 'outline'}
                  size="sm"
                  onClick={() => setTool('move')}
                  className="flex flex-col h-auto py-2"
                >
                  <Move className="w-4 h-4 mb-1" />
                  <span className="text-xs">Move</span>
                </Button>
              </div>

              <div className="border-t pt-2 mt-2 space-y-2">
                <Button
                  variant="outline"
                  size="sm"
                  onClick={handleUndo}
                  disabled={points.length === 0}
                  className="w-full"
                >
                  <RotateCcw className="w-4 h-4 mr-2" />
                  Undo
                </Button>
                <Button
                  variant="outline"
                  size="sm"
                  onClick={handleClear}
                  disabled={points.length === 0}
                  className="w-full text-destructive hover:text-destructive"
                >
                  <Trash2 className="w-4 h-4 mr-2" />
                  Clear All
                </Button>
                {selectedPointIndex !== null && (
                  <Button
                    variant="destructive"
                    size="sm"
                    onClick={handleDeletePoint}
                    className="w-full"
                  >
                    <Trash2 className="w-4 h-4 mr-2" />
                    Delete Point
                  </Button>
                )}
              </div>
            </CardContent>
          </Card>

          {/* Measurements */}
          <Card>
            <CardHeader className="pb-3">
              <CardTitle className="text-sm flex items-center gap-2">
                <Maximize2 className="w-4 h-4" />
                Measurements
              </CardTitle>
            </CardHeader>
            <CardContent className="space-y-3">
              <div className="grid grid-cols-2 gap-2 text-sm">
                <div className="text-muted-foreground">Points:</div>
                <div className="font-medium">{points.length}</div>
                
                <div className="text-muted-foreground">Area:</div>
                <div className="font-medium">
                  {area < 10000 
                    ? `${area.toFixed(1)} m²` 
                    : `${(area / 10000).toFixed(2)} ha`}
                </div>
                
                <div className="text-muted-foreground">Perimeter:</div>
                <div className="font-medium">{perimeter.toFixed(1)} m</div>
                
                <div className="text-muted-foreground">Width:</div>
                <div className="font-medium">{boundingBox.width.toFixed(1)} m</div>
                
                <div className="text-muted-foreground">Height:</div>
                <div className="font-medium">{boundingBox.height.toFixed(1)} m</div>
              </div>

              {isClosed && (
                <div className="bg-green-50 dark:bg-green-900/20 border border-green-200 dark:border-green-800 rounded-lg p-2 text-center">
                  <span className="text-green-700 dark:text-green-400 text-sm font-medium">
                    ✓ Shape Complete
                  </span>
                </div>
              )}
            </CardContent>
          </Card>

          {/* Instructions */}
          <Card>
            <CardHeader className="pb-3">
              <CardTitle className="text-sm flex items-center gap-2">
                <Info className="w-4 h-4" />
                Instructions
              </CardTitle>
            </CardHeader>
            <CardContent className="text-xs text-muted-foreground space-y-2">
              <p><strong>1.</strong> Set your grid scale (meters per square)</p>
              <p><strong>2.</strong> Click on the canvas to place points</p>
              <p><strong>3.</strong> Click near the first point to close the shape</p>
              <p><strong>4.</strong> Drag points to adjust after closing</p>
              <p className="text-primary"><strong>Tip:</strong> Points snap to grid intersections</p>
            </CardContent>
          </Card>
        </div>

        {/* Canvas Area */}
        <div className="lg:col-span-3">
          <Card>
            <CardContent className="p-2">
              <div 
                ref={containerRef}
                className="border rounded-lg overflow-hidden bg-white cursor-crosshair"
                style={{ minHeight: '500px' }}
              >
                <Stage
                  ref={stageRef}
                  width={stageSize.width}
                  height={stageSize.height}
                  onClick={handleStageClick}
                  style={{ 
                    cursor: tool === 'draw' && !isClosed ? 'crosshair' : 
                            tool === 'move' ? 'move' : 'default'
                  }}
                >
                  <Layer>
                    {/* Grid */}
                    {gridLines}

                    {/* Scale indicator */}
                    <Group x={10} y={stageSize.height - 40}>
                      <Rect
                        width={gridSize}
                        height={20}
                        fill="#3b82f6"
                        cornerRadius={2}
                      />
                      <Text
                        x={gridSize + 8}
                        y={4}
                        text={`${gridScale}m`}
                        fontSize={12}
                        fill="#374151"
                      />
                    </Group>

                    {/* Polygon fill (when closed) */}
                    {isClosed && points.length >= 3 && (
                      <Line
                        points={linePoints}
                        fill="rgba(34, 197, 94, 0.2)"
                        stroke="#22c55e"
                        strokeWidth={2}
                        closed={true}
                      />
                    )}

                    {/* Lines connecting points */}
                    {points.length >= 2 && !isClosed && (
                      <Line
                        points={linePoints}
                        stroke="#3b82f6"
                        strokeWidth={2}
                        lineCap="round"
                        lineJoin="round"
                      />
                    )}

                    {/* Points */}
                    {points.map((point, index) => (
                      <Circle
                        key={index}
                        x={point.x * gridSize}
                        y={point.y * gridSize}
                        radius={index === selectedPointIndex ? 10 : 8}
                        fill={index === 0 ? '#22c55e' : 
                              index === selectedPointIndex ? '#ef4444' : '#3b82f6'}
                        stroke="white"
                        strokeWidth={2}
                        draggable={tool === 'select' || tool === 'move'}
                        onDragEnd={(e) => handlePointDrag(index, e)}
                        onClick={(e) => {
                          e.cancelBubble = true;
                          setSelectedPointIndex(index === selectedPointIndex ? null : index);
                        }}
                        onMouseEnter={(e) => {
                          e.target.getStage().container().style.cursor = 'pointer';
                        }}
                        onMouseLeave={(e) => {
                          e.target.getStage().container().style.cursor = 
                            tool === 'draw' && !isClosed ? 'crosshair' : 'default';
                        }}
                      />
                    ))}

                    {/* Point labels */}
                    {points.map((point, index) => (
                      <Text
                        key={`label-${index}`}
                        x={point.x * gridSize + 12}
                        y={point.y * gridSize - 8}
                        text={`${index + 1}`}
                        fontSize={11}
                        fill="#6b7280"
                      />
                    ))}

                    {/* Dimension labels on edges (when closed) */}
                    {isClosed && points.length >= 2 && points.map((point, index) => {
                      const nextIndex = (index + 1) % points.length;
                      const nextPoint = points[nextIndex];
                      const midX = ((point.x + nextPoint.x) / 2) * gridSize;
                      const midY = ((point.y + nextPoint.y) / 2) * gridSize;
                      const dx = nextPoint.x - point.x;
                      const dy = nextPoint.y - point.y;
                      const length = Math.sqrt(dx * dx + dy * dy) * gridScale;
                      
                      return (
                        <Group key={`dim-${index}`}>
                          <Rect
                            x={midX - 20}
                            y={midY - 8}
                            width={40}
                            height={16}
                            fill="rgba(255,255,255,0.9)"
                            cornerRadius={3}
                          />
                          <Text
                            x={midX - 18}
                            y={midY - 5}
                            text={`${length.toFixed(1)}m`}
                            fontSize={10}
                            fill="#374151"
                          />
                        </Group>
                      );
                    })}
                  </Layer>
                </Stage>
              </div>
            </CardContent>
          </Card>

          {/* Status bar */}
          <div className="flex items-center justify-between mt-2 px-2 text-sm text-muted-foreground">
            <span>
              {tool === 'draw' && !isClosed && 'Click to add points. Click near first point (green) to close shape.'}
              {tool === 'select' && 'Click points to select. Drag to move.'}
              {tool === 'move' && 'Drag points to reposition.'}
              {isClosed && tool === 'draw' && 'Shape complete. Switch to Select mode to adjust.'}
            </span>
            <span>
              Scale: 1 square = {gridScale}m × {gridScale}m
            </span>
          </div>

          {/* Next Step Button */}
          {isClosed && (
            <div className="flex justify-end mt-4">
              <Button onClick={() => setActiveTab('details')}>
                Continue to Garden Details
                <ChevronRight className="w-4 h-4 ml-2" />
              </Button>
            </div>
          )}
        </div>
      </div>
      )}

      {/* Step 2: Garden Details Form */}
      {activeTab === 'details' && (
        <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
          {/* Left Column - Location & Environment */}
          <div className="space-y-6">
            {/* GPS Location */}
            <Card>
              <CardHeader>
                <CardTitle className="flex items-center gap-2">
                  <MapPin className="w-5 h-5" />
                  Location (GPS Coordinates)
                </CardTitle>
                <CardDescription>
                  Enter your garden's coordinates for accurate sun path calculation
                </CardDescription>
              </CardHeader>
              <CardContent className="space-y-4">
                <div className="grid grid-cols-2 gap-4">
                  <div className="space-y-2">
                    <Label htmlFor="latitude">Latitude</Label>
                    <Input
                      id="latitude"
                      type="number"
                      step="any"
                      placeholder="e.g., 52.3676"
                      value={gardenDetails.latitude}
                      onChange={(e) => updateGardenDetails('latitude', e.target.value)}
                    />
                  </div>
                  <div className="space-y-2">
                    <Label htmlFor="longitude">Longitude</Label>
                    <Input
                      id="longitude"
                      type="number"
                      step="any"
                      placeholder="e.g., 4.9041"
                      value={gardenDetails.longitude}
                      onChange={(e) => updateGardenDetails('longitude', e.target.value)}
                    />
                  </div>
                </div>
                <p className="text-xs text-muted-foreground">
                  <strong>Tip:</strong> You can find your coordinates on Google Maps by right-clicking your location
                </p>
                {gardenDetails.latitude && gardenDetails.longitude && (
                  <div className="bg-muted/50 rounded-lg p-3 text-sm">
                    <div className="flex items-center gap-2">
                      <Sun className="w-4 h-4 text-yellow-500" />
                      <span>AI will calculate sun path, angles, and climate for this location</span>
                    </div>
                  </div>
                )}
              </CardContent>
            </Card>

            {/* Wind Direction */}
            <Card>
              <CardHeader>
                <CardTitle className="flex items-center gap-2">
                  <Wind className="w-5 h-5" />
                  Prevailing Wind Direction
                </CardTitle>
                <CardDescription>
                  Select the direction wind usually comes from
                </CardDescription>
              </CardHeader>
              <CardContent>
                <div className="grid grid-cols-4 gap-2">
                  {windDirections.map((dir) => (
                    <Button
                      key={dir.value}
                      variant={gardenDetails.windDirection === dir.value ? 'default' : 'outline'}
                      className="flex flex-col h-auto py-3"
                      onClick={() => updateGardenDetails('windDirection', dir.value)}
                    >
                      <Compass 
                        className="w-5 h-5 mb-1" 
                        style={{ transform: `rotate(${dir.angle}deg)` }}
                      />
                      <span className="text-xs">{dir.label}</span>
                    </Button>
                  ))}
                </div>
              </CardContent>
            </Card>

            {/* Garden Goal */}
            <Card>
              <CardHeader>
                <CardTitle className="flex items-center gap-2">
                  <Target className="w-5 h-5" />
                  Garden Goal
                </CardTitle>
                <CardDescription>
                  What type of garden do you want to create?
                </CardDescription>
              </CardHeader>
              <CardContent className="space-y-3">
                {gardenGoals.map((goal) => {
                  const Icon = goal.icon;
                  return (
                    <div
                      key={goal.value}
                      className={`p-4 rounded-lg border-2 cursor-pointer transition-all ${
                        gardenDetails.gardenGoal === goal.value
                          ? 'border-primary bg-primary/5'
                          : 'border-border hover:border-primary/50'
                      }`}
                      onClick={() => updateGardenDetails('gardenGoal', goal.value)}
                    >
                      <div className="flex items-start gap-3">
                        <Icon className={`w-5 h-5 mt-0.5 ${
                          gardenDetails.gardenGoal === goal.value ? 'text-primary' : 'text-muted-foreground'
                        }`} />
                        <div>
                          <div className="font-medium">{goal.label}</div>
                          <div className="text-sm text-muted-foreground">{goal.description}</div>
                        </div>
                      </div>
                    </div>
                  );
                })}
              </CardContent>
            </Card>
          </div>

          {/* Right Column - Plants & Features */}
          <div className="space-y-6">
            {/* Plant Preferences */}
            <Card>
              <CardHeader>
                <CardTitle className="flex items-center gap-2">
                  <Leaf className="w-5 h-5" />
                  What do you want to grow?
                </CardTitle>
                <CardDescription>
                  Select all that apply
                </CardDescription>
              </CardHeader>
              <CardContent className="space-y-4">
                <div className="flex flex-wrap gap-2">
                  {plantOptions.map((plant) => (
                    <Badge
                      key={plant.id}
                      variant={gardenDetails.plantPreferences.includes(plant.id) ? 'default' : 'outline'}
                      className="cursor-pointer py-2 px-3"
                      onClick={() => togglePlantPreference(plant.id)}
                    >
                      {gardenDetails.plantPreferences.includes(plant.id) && (
                        <span className="mr-1">✓</span>
                      )}
                      {plant.label}
                    </Badge>
                  ))}
                </div>
                
                {gardenDetails.plantPreferences.length > 0 && (
                  <div className="bg-muted/50 rounded-lg p-3 text-sm">
                    <strong>Selected:</strong>{' '}
                    {gardenDetails.plantPreferences.map(id => 
                      plantOptions.find(p => p.id === id)?.label
                    ).join(', ')}
                  </div>
                )}

                <div className="space-y-2">
                  <Label htmlFor="customPlants">Specific plants (optional)</Label>
                  <Textarea
                    id="customPlants"
                    placeholder="List any specific plants you want, e.g., Roma tomatoes, Gala apples, Meyer lemons..."
                    value={gardenDetails.customPlants}
                    onChange={(e) => updateGardenDetails('customPlants', e.target.value)}
                    rows={3}
                  />
                </div>
              </CardContent>
            </Card>

            {/* Existing Features */}
            <Card>
              <CardHeader>
                <CardTitle className="flex items-center gap-2">
                  <Home className="w-5 h-5" />
                  Existing Features on Land
                </CardTitle>
                <CardDescription>
                  What's already on your property? (optional)
                </CardDescription>
              </CardHeader>
              <CardContent className="space-y-4">
                <div className="grid grid-cols-2 gap-2">
                  {featureOptions.map((feature) => {
                    const Icon = feature.icon;
                    return (
                      <Button
                        key={feature.id}
                        variant={gardenDetails.existingFeatures.includes(feature.id) ? 'default' : 'outline'}
                        className="justify-start h-auto py-3"
                        onClick={() => toggleFeature(feature.id)}
                      >
                        <Icon className="w-4 h-4 mr-2" />
                        {feature.label}
                      </Button>
                    );
                  })}
                </div>

                <div className="space-y-2">
                  <Label htmlFor="customFeatures">Other features (optional)</Label>
                  <Textarea
                    id="customFeatures"
                    placeholder="Describe any other features: greenhouse, compost area, chicken coop, etc."
                    value={gardenDetails.customFeatures}
                    onChange={(e) => updateGardenDetails('customFeatures', e.target.value)}
                    rows={2}
                  />
                </div>
              </CardContent>
            </Card>

            {/* Additional Notes */}
            <Card>
              <CardHeader>
                <CardTitle className="flex items-center gap-2">
                  <Info className="w-5 h-5" />
                  Additional Notes
                </CardTitle>
              </CardHeader>
              <CardContent>
                <Textarea
                  placeholder="Any other information the AI should consider: soil type, water availability, time constraints, budget, etc."
                  value={gardenDetails.notes}
                  onChange={(e) => updateGardenDetails('notes', e.target.value)}
                  rows={4}
                />
              </CardContent>
            </Card>

            {/* Summary & Continue */}
            <Card className={isFormValid() ? 'border-green-500 bg-green-50 dark:bg-green-900/20' : ''}>
              <CardContent className="pt-6">
                <div className="space-y-3">
                  <h4 className="font-medium">Summary</h4>
                  <div className="text-sm space-y-1">
                    <div className="flex items-center gap-2">
                      {isClosed ? '✓' : '○'} Garden boundary: {area.toFixed(1)} m² ({points.length} points)
                    </div>
                    <div className="flex items-center gap-2">
                      {gardenDetails.latitude && gardenDetails.longitude ? '✓' : '○'} Location set
                    </div>
                    <div className="flex items-center gap-2">
                      {gardenDetails.windDirection ? '✓' : '○'} Wind direction: {gardenDetails.windDirection || 'Not set'}
                    </div>
                    <div className="flex items-center gap-2">
                      {gardenDetails.gardenGoal ? '✓' : '○'} Garden type: {
                        gardenGoals.find(g => g.value === gardenDetails.gardenGoal)?.label || 'Not selected'
                      }
                    </div>
                    <div className="flex items-center gap-2">
                      {gardenDetails.plantPreferences.length > 0 ? '✓' : '○'} Plants: {
                        gardenDetails.plantPreferences.length > 0 
                          ? `${gardenDetails.plantPreferences.length} categories`
                          : 'None selected'
                      }
                    </div>
                  </div>

                  <div className="flex gap-2 pt-2">
                    <Button variant="outline" onClick={() => setActiveTab('draw')}>
                      <ArrowLeft className="w-4 h-4 mr-2" />
                      Back to Drawing
                    </Button>
                    <Button 
                      className="flex-1"
                      disabled={!isFormValid()}
                      onClick={() => setActiveTab('generate')}
                    >
                      <Sparkles className="w-4 h-4 mr-2" />
                      Generate Garden Design
                      <ChevronRight className="w-4 h-4 ml-2" />
                    </Button>
                  </div>
                </div>
              </CardContent>
            </Card>
          </div>
        </div>
      )}

      {/* Step 3: Generate (Placeholder for Phase 3) */}
      {activeTab === 'generate' && (
        <Card className="max-w-2xl mx-auto">
          <CardHeader className="text-center">
            <CardTitle className="flex items-center justify-center gap-2">
              <Sparkles className="w-6 h-6" />
              Ready to Generate Your Garden Design
            </CardTitle>
            <CardDescription>
              AI will analyze your inputs and create a personalized garden layout
            </CardDescription>
          </CardHeader>
          <CardContent className="space-y-6">
            <div className="bg-muted/50 rounded-lg p-4 space-y-2 text-sm">
              <div><strong>Garden Size:</strong> {area.toFixed(1)} m² ({boundingBox.width.toFixed(1)}m × {boundingBox.height.toFixed(1)}m)</div>
              <div><strong>Location:</strong> {gardenDetails.latitude}, {gardenDetails.longitude}</div>
              <div><strong>Wind:</strong> From the {windDirections.find(w => w.value === gardenDetails.windDirection)?.label}</div>
              <div><strong>Type:</strong> {gardenGoals.find(g => g.value === gardenDetails.gardenGoal)?.label}</div>
              <div><strong>Plants:</strong> {gardenDetails.plantPreferences.map(id => 
                plantOptions.find(p => p.id === id)?.label
              ).join(', ')}</div>
              {gardenDetails.customPlants && <div><strong>Specific:</strong> {gardenDetails.customPlants}</div>}
            </div>

            <div className="text-center text-muted-foreground">
              <p>Phase 3 (AI Generation) will be implemented next.</p>
              <p className="text-sm mt-2">This will use your OpenAI API key to generate the design.</p>
            </div>

            <div className="flex gap-2">
              <Button variant="outline" onClick={() => setActiveTab('details')}>
                <ArrowLeft className="w-4 h-4 mr-2" />
                Back to Details
              </Button>
              <Button className="flex-1" disabled>
                <Sparkles className="w-4 h-4 mr-2" />
                Generate Design (Coming in Phase 3)
              </Button>
            </div>
          </CardContent>
        </Card>
      )}
    </div>
  );
};

export default GardenDesignerPage;
