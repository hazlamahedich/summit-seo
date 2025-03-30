"""JavaScript processor module for analyzing JavaScript content."""

import re
import json
from typing import Dict, Any, List, Optional
from .base import BaseProcessor, TransformationError

class JavaScriptProcessor(BaseProcessor):
    """Processor for analyzing JavaScript content."""
    
    def __init__(self, config: Optional[Dict[str, Any]] = None):
        """Initialize the JavaScript processor.
        
        Args:
            config: Optional configuration dictionary with settings:
                - minify: Whether to minify the JavaScript (default: False)
                - extract_json: Whether to extract JSON data (default: True)
                - analyze_imports: Whether to analyze import statements (default: True)
                - detect_libraries: Whether to detect JavaScript libraries (default: True)
                - count_functions: Whether to count functions (default: True)
                - analyze_events: Whether to analyze event listeners (default: True)
        """
        super().__init__(config)
        self.minify = self.config.get('minify', False)
        self.extract_json = self.config.get('extract_json', True)
        self.analyze_imports = self.config.get('analyze_imports', True)
        self.detect_libraries = self.config.get('detect_libraries', True)
        self.count_functions = self.config.get('count_functions', True)
        self.analyze_events = self.config.get('analyze_events', True)
    
    def _validate_config(self) -> None:
        """Validate processor configuration."""
        bool_keys = [
            'minify', 'extract_json', 'analyze_imports', 
            'detect_libraries', 'count_functions', 'analyze_events'
        ]
        
        for key in bool_keys:
            if key in self.config and not isinstance(self.config[key], bool):
                raise ValueError(f"{key} must be a boolean")
    
    def _get_required_fields(self) -> List[str]:
        """Get list of required input fields."""
        return ['javascript_content']
    
    async def _process_data(self, data: Dict[str, Any]) -> Dict[str, Any]:
        """Process JavaScript content.
        
        Args:
            data: Dictionary containing JavaScript content.
            
        Returns:
            Dictionary with processed JavaScript and extracted data.
            
        Raises:
            TransformationError: If JavaScript processing fails.
        """
        try:
            js_content = data['javascript_content']
            processed_data = {
                'original_size': len(js_content),
                'line_count': js_content.count('\n') + 1
            }
            
            # Minify JavaScript if configured
            if self.minify:
                minified_js = self._minify_javascript(js_content)
                processed_data['minified_content'] = minified_js
                processed_data['minified_size'] = len(minified_js)
                processed_data['size_reduction'] = round(
                    (1 - len(minified_js) / len(js_content)) * 100, 2
                )
            else:
                processed_data['processed_content'] = js_content
            
            # Extract JSON data if configured
            if self.extract_json:
                json_data = self._extract_json_data(js_content)
                processed_data['json_objects'] = json_data
            
            # Analyze imports if configured
            if self.analyze_imports:
                imports = self._analyze_imports(js_content)
                processed_data['imports'] = imports
            
            # Detect JavaScript libraries if configured
            if self.detect_libraries:
                libraries = self._detect_libraries(js_content)
                processed_data['libraries'] = libraries
            
            # Count functions if configured
            if self.count_functions:
                function_stats = self._count_functions(js_content)
                processed_data['function_stats'] = function_stats
            
            # Analyze event listeners if configured
            if self.analyze_events:
                events = self._analyze_events(js_content)
                processed_data['events'] = events
            
            return processed_data
            
        except Exception as e:
            raise TransformationError(f"JavaScript processing failed: {str(e)}")
    
    def _minify_javascript(self, js_content: str) -> str:
        """Minify JavaScript content.
        
        Args:
            js_content: JavaScript content to minify.
            
        Returns:
            Minified JavaScript content.
        """
        # Remove comments
        js_content = re.sub(r'//.*?\n', '\n', js_content)
        js_content = re.sub(r'/\*.*?\*/', '', js_content, flags=re.DOTALL)
        
        # Remove whitespace
        js_content = re.sub(r'\s+', ' ', js_content)
        
        # Remove unnecessary semicolons
        js_content = re.sub(r';\s*;', ';', js_content)
        
        # Remove spaces around operators
        js_content = re.sub(r'\s*([=+\-*/<>!&|:;,(){}[\]])\s*', r'\1', js_content)
        
        return js_content.strip()
    
    def _extract_json_data(self, js_content: str) -> List[Dict[str, Any]]:
        """Extract JSON data from JavaScript content.
        
        Args:
            js_content: JavaScript content.
            
        Returns:
            List of extracted JSON objects.
        """
        # Find JSON objects
        json_objects = []
        
        # Look for JSON object definitions
        json_pattern = r'(?:const|let|var)\s+(\w+)\s*=\s*({[\s\S]*?});'
        matches = re.finditer(json_pattern, js_content)
        
        for match in matches:
            variable_name = match.group(1)
            json_str = match.group(2)
            
            try:
                # Try to parse as JSON
                json_obj = json.loads(json_str)
                json_objects.append({
                    'variable': variable_name,
                    'data': json_obj
                })
            except (json.JSONDecodeError, SyntaxError):
                # Not valid JSON, could be a regular JavaScript object
                pass
        
        return json_objects
    
    def _analyze_imports(self, js_content: str) -> Dict[str, List[str]]:
        """Analyze import statements in JavaScript content.
        
        Args:
            js_content: JavaScript content.
            
        Returns:
            Dictionary with import analysis.
        """
        imports = {
            'es6_imports': [],
            'require_imports': [],
            'script_tags': []
        }
        
        # Find ES6 imports
        es6_pattern = r'import\s+(?:{[^}]+}|[^{}\n;]+)\s+from\s+[\'"]([^\'"]+)[\'"]'
        es6_imports = re.findall(es6_pattern, js_content)
        imports['es6_imports'] = es6_imports
        
        # Find require imports
        require_pattern = r'(?:const|let|var)\s+\w+\s*=\s*require\([\'"]([^\'"]+)[\'"]\)'
        require_imports = re.findall(require_pattern, js_content)
        imports['require_imports'] = require_imports
        
        # Find script tag imports
        script_pattern = r'document\.createElement\([\'"]script[\'"]\)[\s\S]*?\.src\s*=\s*[\'"]([^\'"]+)[\'"]'
        script_imports = re.findall(script_pattern, js_content)
        imports['script_tags'] = script_imports
        
        return imports
    
    def _detect_libraries(self, js_content: str) -> List[Dict[str, str]]:
        """Detect JavaScript libraries in the content.
        
        Args:
            js_content: JavaScript content.
            
        Returns:
            List of detected libraries with versions.
        """
        libraries = []
        
        # Common libraries and their detection patterns
        library_patterns = [
            {
                'name': 'jQuery',
                'pattern': r'(?:jQuery|window\.\$|window\.jQuery)(?:\.fn\.version|\s*\.version)\s*=\s*[\'"]([^\'"]+)[\'"]'
            },
            {
                'name': 'React',
                'pattern': r'React\.version\s*=\s*[\'"]([^\'"]+)[\'"]'
            },
            {
                'name': 'Vue',
                'pattern': r'Vue\.version\s*=\s*[\'"]([^\'"]+)[\'"]'
            },
            {
                'name': 'Angular',
                'pattern': r'angular\.version\s*=\s*[\'"]([^\'"]+)[\'"]'
            },
            {
                'name': 'Lodash',
                'pattern': r'_\.VERSION\s*=\s*[\'"]([^\'"]+)[\'"]'
            },
            {
                'name': 'Moment.js',
                'pattern': r'moment\.version\s*=\s*[\'"]([^\'"]+)[\'"]'
            }
        ]
        
        for lib in library_patterns:
            matches = re.search(lib['pattern'], js_content)
            if matches:
                libraries.append({
                    'name': lib['name'],
                    'version': matches.group(1)
                })
            elif re.search(lib['name'].lower(), js_content.lower()):
                # Library might be present but we couldn't detect the version
                libraries.append({
                    'name': lib['name'],
                    'version': 'unknown'
                })
        
        return libraries
    
    def _count_functions(self, js_content: str) -> Dict[str, int]:
        """Count different types of functions in JavaScript content.
        
        Args:
            js_content: JavaScript content.
            
        Returns:
            Dictionary with function counts.
        """
        function_stats = {
            'function_declarations': 0,
            'function_expressions': 0,
            'arrow_functions': 0,
            'async_functions': 0,
            'total_functions': 0
        }
        
        # Function declarations
        function_declarations = re.findall(r'function\s+\w+\s*\(', js_content)
        function_stats['function_declarations'] = len(function_declarations)
        
        # Function expressions
        function_expressions = re.findall(r'(?:const|let|var)\s+\w+\s*=\s*function\s*\(', js_content)
        function_stats['function_expressions'] = len(function_expressions)
        
        # Arrow functions
        arrow_functions = re.findall(r'=>', js_content)
        function_stats['arrow_functions'] = len(arrow_functions)
        
        # Async functions
        async_functions = re.findall(r'async\s+function', js_content)
        function_stats['async_functions'] = len(async_functions)
        
        # Calculate total
        function_stats['total_functions'] = (
            function_stats['function_declarations'] +
            function_stats['function_expressions'] +
            function_stats['arrow_functions']
        )
        
        return function_stats
    
    def _analyze_events(self, js_content: str) -> Dict[str, List[str]]:
        """Analyze event listeners in JavaScript content.
        
        Args:
            js_content: JavaScript content.
            
        Returns:
            Dictionary with event listener analysis.
        """
        events = {
            'addEventListener': [],
            'on_events': [],
            'jquery_events': []
        }
        
        # Find addEventListener calls
        add_event_pattern = r'\.addEventListener\(\s*[\'"](\w+)[\'"]'
        add_events = re.findall(add_event_pattern, js_content)
        events['addEventListener'] = add_events
        
        # Find on* event assignments
        on_event_pattern = r'\.on(\w+)\s*='
        on_events = [f"on{event}" for event in re.findall(on_event_pattern, js_content)]
        events['on_events'] = on_events
        
        # Find jQuery event bindings
        jquery_event_pattern = r'\$\(.*\)\.on\(\s*[\'"](\w+)[\'"]'
        jquery_events = re.findall(jquery_event_pattern, js_content)
        events['jquery_events'] = jquery_events
        
        return events 