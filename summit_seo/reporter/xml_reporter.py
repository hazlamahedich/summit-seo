"""XML reporter module for Summit SEO."""

import xml.dom.minidom as minidom
import xml.etree.ElementTree as ET
from typing import Dict, Any, List, Optional
from datetime import datetime
from .base import BaseReporter, ReportResult, ReportGenerationError

class XMLReporter(BaseReporter):
    """Reporter for generating XML reports."""

    def __init__(self, config: Optional[Dict[str, Any]] = None):
        """Initialize the XML reporter.
        
        Args:
            config: Optional configuration dictionary.
                   Supported keys:
                   - pretty_print: Whether to format XML with indentation (default: True)
                   - include_metadata: Whether to include report metadata (default: True)
                   - indent_spaces: Number of spaces for indentation (default: 2)
                   - xml_declaration: Whether to include XML declaration (default: True)
                   - encoding: XML encoding (default: 'utf-8')
        """
        super().__init__(config)

    def validate_config(self) -> None:
        """Validate the reporter configuration.
        
        Raises:
            ValueError: If configuration is invalid.
        """
        if 'pretty_print' in self.config and not isinstance(self.config['pretty_print'], bool):
            raise ValueError("pretty_print must be a boolean")
        
        if 'include_metadata' in self.config and not isinstance(self.config['include_metadata'], bool):
            raise ValueError("include_metadata must be a boolean")
        
        if 'indent_spaces' in self.config and not isinstance(self.config['indent_spaces'], int):
            raise ValueError("indent_spaces must be an integer")
        
        if 'xml_declaration' in self.config and not isinstance(self.config['xml_declaration'], bool):
            raise ValueError("xml_declaration must be a boolean")
        
        if 'encoding' in self.config and not isinstance(self.config['encoding'], str):
            raise ValueError("encoding must be a string")

    def _format_datetime(self, dt: datetime) -> str:
        """Format datetime object as ISO 8601 string.
        
        Args:
            dt: Datetime object to format.
        
        Returns:
            ISO 8601 formatted string.
        """
        return dt.isoformat()

    def _add_subelements(self, parent: ET.Element, data: Dict[str, Any]) -> None:
        """Add child elements to a parent element recursively.
        
        Args:
            parent: Parent XML element.
            data: Dictionary containing data to add as child elements.
        """
        for key, value in data.items():
            if isinstance(value, dict):
                child = ET.SubElement(parent, key)
                self._add_subelements(child, value)
            elif isinstance(value, list):
                # For lists, create multiple elements with the same tag
                list_parent = ET.SubElement(parent, key + "_list")
                for item in value:
                    if isinstance(item, dict):
                        item_element = ET.SubElement(list_parent, key)
                        self._add_subelements(item_element, item)
                    else:
                        item_element = ET.SubElement(list_parent, key)
                        item_element.text = str(item)
            else:
                child = ET.SubElement(parent, key)
                child.text = str(value)

    def _create_xml_element(self, data: Dict[str, Any], metadata: Optional[Dict[str, Any]] = None) -> ET.Element:
        """Create XML element from analysis data.
        
        Args:
            data: Analysis results data.
            metadata: Optional metadata to include.
            
        Returns:
            XML Element tree containing the report data.
        """
        # Create root element
        root = ET.Element("summit_seo_report")
        
        # Add URL and timestamp
        url_element = ET.SubElement(root, "url")
        url_element.text = data['url']
        
        timestamp_element = ET.SubElement(root, "timestamp")
        timestamp_element.text = str(data['timestamp'])
        
        # Create results element
        results = ET.SubElement(root, "results")
        
        # Format analyzer results
        for analyzer, result in data['results'].items():
            analyzer_element = ET.SubElement(results, "analyzer")
            analyzer_element.set("name", analyzer)
            
            score_element = ET.SubElement(analyzer_element, "score")
            score_element.text = str(result['score'])
            
            # Add issues
            issues = result.get('issues', [])
            if issues:
                issues_element = ET.SubElement(analyzer_element, "issues")
                for issue in issues:
                    issue_element = ET.SubElement(issues_element, "issue")
                    issue_element.text = issue
            
            # Add warnings
            warnings = result.get('warnings', [])
            if warnings:
                warnings_element = ET.SubElement(analyzer_element, "warnings")
                for warning in warnings:
                    warning_element = ET.SubElement(warnings_element, "warning")
                    warning_element.text = warning
            
            # Add suggestions
            suggestions = result.get('suggestions', [])
            if suggestions:
                suggestions_element = ET.SubElement(analyzer_element, "suggestions")
                for suggestion in suggestions:
                    suggestion_element = ET.SubElement(suggestions_element, "suggestion")
                    suggestion_element.text = suggestion
        
        # Include metadata if configured
        if self.config.get('include_metadata', True) and metadata:
            metadata_element = ET.SubElement(root, "metadata")
            for key, value in metadata.items():
                meta_item = ET.SubElement(metadata_element, key)
                meta_item.text = str(value)
        
        return root

    async def generate_report(self, data: Dict[str, Any]) -> ReportResult:
        """Generate an XML report from the analysis results.
        
        Args:
            data: Dictionary containing analysis results.
        
        Returns:
            ReportResult containing the generated XML and metadata.
        
        Raises:
            ReportGenerationError: If report generation fails.
        """
        try:
            self._validate_data(data)
            
            metadata = self._create_metadata('xml')
            
            # Create XML structure
            root = self._create_xml_element(
                data,
                metadata.__dict__ if self.config.get('include_metadata', True) else None
            )
            
            # Generate XML string
            xml_string = ET.tostring(
                root, 
                encoding=self.config.get('encoding', 'utf-8')
            ).decode('utf-8')
            
            # Pretty print if configured
            if self.config.get('pretty_print', True):
                dom = minidom.parseString(xml_string)
                xml_string = dom.toprettyxml(
                    indent=' ' * self.config.get('indent_spaces', 2),
                    encoding=self.config.get('encoding', 'utf-8')
                ).decode('utf-8')
                
                # Remove extra empty lines that minidom tends to add
                xml_string = '\n'.join(line for line in xml_string.split('\n') if line.strip())
            
            # Add XML declaration if configured
            if not self.config.get('xml_declaration', True):
                xml_string = xml_string.split('\n', 1)[1]
            
            return ReportResult(
                content=xml_string,
                metadata=metadata,
                format='xml'
            )
            
        except Exception as e:
            raise ReportGenerationError(f"Failed to generate XML report: {str(e)}")

    async def generate_batch_report(self, data: List[Dict[str, Any]]) -> ReportResult:
        """Generate an XML report for multiple analysis results.
        
        Args:
            data: List of dictionaries containing analysis results.
        
        Returns:
            ReportResult containing the generated XML and metadata.
        
        Raises:
            ReportGenerationError: If report generation fails.
        """
        try:
            self._validate_batch_data(data)
            
            metadata = self._create_metadata('xml')
            
            # Create root element for batch report
            root = ET.Element("summit_seo_batch_report")
            
            # Add batch metadata
            type_element = ET.SubElement(root, "type")
            type_element.text = "batch_report"
            
            count_element = ET.SubElement(root, "count")
            count_element.text = str(len(data))
            
            timestamp_element = ET.SubElement(root, "timestamp")
            timestamp_element.text = self._format_datetime(datetime.utcnow())
            
            # Create results container
            results_element = ET.SubElement(root, "results")
            
            # Process each result
            for item in data:
                report_element = ET.SubElement(results_element, "report")
                
                url_element = ET.SubElement(report_element, "url")
                url_element.text = item['url']
                
                item_timestamp = ET.SubElement(report_element, "timestamp")
                item_timestamp.text = str(item['timestamp'])
                
                # Add analyzer results
                item_results = ET.SubElement(report_element, "analyzers")
                for analyzer, result in item['results'].items():
                    analyzer_element = ET.SubElement(item_results, "analyzer")
                    analyzer_element.set("name", analyzer)
                    
                    score_element = ET.SubElement(analyzer_element, "score")
                    score_element.text = str(result['score'])
                    
                    # Add issues, warnings, suggestions
                    for category in ['issues', 'warnings', 'suggestions']:
                        items = result.get(category, [])
                        if items:
                            category_element = ET.SubElement(analyzer_element, category)
                            for item_text in items:
                                item_element = ET.SubElement(category_element, category[:-1])  # Remove 's' for singular
                                item_element.text = item_text
            
            # Include metadata if configured
            if self.config.get('include_metadata', True):
                metadata_element = ET.SubElement(root, "metadata")
                for key, value in metadata.__dict__.items():
                    meta_item = ET.SubElement(metadata_element, key)
                    meta_item.text = str(value)
            
            # Generate XML string
            xml_string = ET.tostring(
                root, 
                encoding=self.config.get('encoding', 'utf-8')
            ).decode('utf-8')
            
            # Pretty print if configured
            if self.config.get('pretty_print', True):
                dom = minidom.parseString(xml_string)
                xml_string = dom.toprettyxml(
                    indent=' ' * self.config.get('indent_spaces', 2),
                    encoding=self.config.get('encoding', 'utf-8')
                ).decode('utf-8')
                
                # Remove extra empty lines that minidom tends to add
                xml_string = '\n'.join(line for line in xml_string.split('\n') if line.strip())
            
            # Add XML declaration if configured
            if not self.config.get('xml_declaration', True):
                xml_string = xml_string.split('\n', 1)[1]
            
            return ReportResult(
                content=xml_string,
                metadata=metadata,
                format='xml'
            )
            
        except Exception as e:
            raise ReportGenerationError(f"Failed to generate batch XML report: {str(e)}") 