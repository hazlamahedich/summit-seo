"""PDF reporter module for generating SEO analysis reports in PDF format."""

import os
import tempfile
from typing import Dict, Any, List, Optional, Tuple
from datetime import datetime
import json
import base64
from pathlib import Path

from .base import BaseReporter, ReportGenerationError, ReportResult, ReportMetadata

class PDFReporter(BaseReporter):
    """Reporter for generating PDF reports from SEO analysis data."""
    
    def __init__(self, config: Optional[Dict[str, Any]] = None):
        """Initialize the PDF reporter.
        
        Args:
            config: Optional configuration dictionary with settings:
                - output_path: Path to save the PDF file (default: "seo_report.pdf")
                - title: Title for the report (default: "SEO Analysis Report")
                - include_charts: Whether to include charts/graphs (default: True)
                - include_recommendations: Whether to include recommendations (default: True)
                - include_details: Whether to include detailed results (default: True)
                - include_summary: Whether to include summary section (default: True)
                - theme: Report theme (default: "default", options: "default", "dark", "light")
                - page_size: Page size (default: "A4", options: "A4", "Letter", "Legal")
                - logo_path: Path to logo image file for branding (optional)
        """
        super().__init__(config)
        
        # Set reporter configuration with defaults
        self.output_path = self.config.get('output_path', 'seo_report.pdf')
        self.title = self.config.get('title', 'SEO Analysis Report')
        self.include_charts = self.config.get('include_charts', True)
        self.include_recommendations = self.config.get('include_recommendations', True)
        self.include_details = self.config.get('include_details', True)
        self.include_summary = self.config.get('include_summary', True)
        self.theme = self.config.get('theme', 'default')
        self.page_size = self.config.get('page_size', 'A4')
        self.logo_path = self.config.get('logo_path', None)
    
    def _validate_config(self) -> None:
        """Validate reporter configuration."""
        # Validate boolean values
        for key in ('include_charts', 'include_recommendations', 
                   'include_details', 'include_summary'):
            if key in self.config and not isinstance(self.config[key], bool):
                raise ValueError(f"{key} must be a boolean")
        
        # Validate theme value
        if 'theme' in self.config and self.config['theme'] not in ('default', 'dark', 'light'):
            raise ValueError("theme must be one of: 'default', 'dark', 'light'")
        
        # Validate page size value
        if 'page_size' in self.config and self.config['page_size'] not in ('A4', 'Letter', 'Legal'):
            raise ValueError("page_size must be one of: 'A4', 'Letter', 'Legal'")
        
        # Validate logo_path if provided
        if self.logo_path and not os.path.isfile(self.logo_path):
            raise ValueError(f"Logo file not found at {self.logo_path}")
    
    async def generate_report(self, data: Dict[str, Any]) -> Dict[str, Any]:
        """Generate a PDF report from analysis data.
        
        Args:
            data: Dictionary containing analysis results.
            
        Returns:
            Dictionary with report information.
            
        Raises:
            ReportGenerationError: If PDF generation fails.
        """
        try:
            # Try to import reportlab - we do this here to avoid making it a hard dependency
            try:
                from reportlab.lib.pagesizes import A4, LETTER, LEGAL
                from reportlab.lib import colors
                from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
                from reportlab.lib.units import inch, cm
                from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle, Image
                from reportlab.platypus import PageBreak, ListFlowable, ListItem
                from reportlab.pdfgen import canvas
            except ImportError:
                raise ReportGenerationError("ReportLab library not installed. Please install with 'pip install reportlab'")
            
            # Set page size
            page_size_map = {
                'A4': A4,
                'Letter': LETTER,
                'Legal': LEGAL
            }
            page_size = page_size_map.get(self.page_size, A4)
            
            # Set theme colors
            theme_colors = {
                'default': {
                    'heading': colors.HexColor('#003366'),
                    'subheading': colors.HexColor('#336699'),
                    'text': colors.black,
                    'line': colors.HexColor('#CCCCCC'),
                    'table_head': colors.HexColor('#EEEEEE'),
                    'good': colors.HexColor('#00AA00'),
                    'warning': colors.HexColor('#FF9900'),
                    'error': colors.HexColor('#CC0000')
                },
                'dark': {
                    'heading': colors.HexColor('#FFFFFF'),
                    'subheading': colors.HexColor('#CCCCCC'),
                    'text': colors.HexColor('#EEEEEE'),
                    'line': colors.HexColor('#666666'),
                    'table_head': colors.HexColor('#333333'),
                    'good': colors.HexColor('#66CC66'),
                    'warning': colors.HexColor('#FFCC66'),
                    'error': colors.HexColor('#FF6666')
                },
                'light': {
                    'heading': colors.HexColor('#006699'),
                    'subheading': colors.HexColor('#3399CC'),
                    'text': colors.HexColor('#333333'),
                    'line': colors.HexColor('#DDDDDD'),
                    'table_head': colors.HexColor('#F5F5F5'),
                    'good': colors.HexColor('#00CC00'),
                    'warning': colors.HexColor('#FFCC00'),
                    'error': colors.HexColor('#FF0000')
                }
            }
            colors_theme = theme_colors.get(self.theme, theme_colors['default'])
            
            # Create document elements list
            elements = []
            
            # Get styles
            styles = getSampleStyleSheet()
            styles.add(ParagraphStyle(
                name='Heading1',
                parent=styles['Heading1'],
                textColor=colors_theme['heading'],
                spaceAfter=12
            ))
            styles.add(ParagraphStyle(
                name='Heading2',
                parent=styles['Heading2'],
                textColor=colors_theme['subheading'],
                spaceAfter=10
            ))
            styles.add(ParagraphStyle(
                name='Normal',
                parent=styles['Normal'],
                textColor=colors_theme['text'],
                spaceBefore=6,
                spaceAfter=6
            ))
            styles.add(ParagraphStyle(
                name='Good',
                parent=styles['Normal'],
                textColor=colors_theme['good']
            ))
            styles.add(ParagraphStyle(
                name='Warning',
                parent=styles['Normal'],
                textColor=colors_theme['warning']
            ))
            styles.add(ParagraphStyle(
                name='Error',
                parent=styles['Normal'],
                textColor=colors_theme['error']
            ))
            
            # Create document title
            if self.logo_path:
                try:
                    logo = Image(self.logo_path, width=1.5*inch, height=0.5*inch)
                    elements.append(logo)
                    elements.append(Spacer(1, 12))
                except Exception as e:
                    # If logo fails, just continue without it
                    pass
            
            elements.append(Paragraph(self.title, styles['Heading1']))
            elements.append(Spacer(1, 12))
            
            # Add report generation info
            elements.append(Paragraph(f"Generated: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}", styles['Normal']))
            if 'url' in data:
                elements.append(Paragraph(f"URL: {data['url']}", styles['Normal']))
            elements.append(Spacer(1, 24))
            
            # Add summary section
            if self.include_summary and 'summary' in data:
                elements.append(Paragraph("Summary", styles['Heading2']))
                
                summary = data.get('summary', {})
                if isinstance(summary, dict):
                    # Create summary table
                    table_data = []
                    table_data.append(["Metric", "Value", "Rating"])
                    
                    # Add important metrics
                    metrics = [
                        ('score', 'Overall Score'),
                        ('performance', 'Performance'),
                        ('accessibility', 'Accessibility'),
                        ('best_practices', 'Best Practices'),
                        ('seo', 'SEO')
                    ]
                    
                    for key, label in metrics:
                        if key in summary:
                            value = summary[key]
                            if isinstance(value, (int, float)):
                                # Format numeric values with rating
                                if value >= 90:
                                    rating = "Excellent"
                                    style = "Good"
                                elif value >= 70:
                                    rating = "Good"
                                    style = "Good"
                                elif value >= 50:
                                    rating = "Average"
                                    style = "Warning"
                                else:
                                    rating = "Poor"
                                    style = "Error"
                                
                                table_data.append([
                                    label, 
                                    f"{value:.1f}" if isinstance(value, float) else str(value),
                                    Paragraph(rating, styles[style])
                                ])
                    
                    # Add the table if it has data beyond the header
                    if len(table_data) > 1:
                        table = Table(table_data, colWidths=[3*cm, 3*cm, 3*cm])
                        table.setStyle(TableStyle([
                            ('BACKGROUND', (0, 0), (-1, 0), colors_theme['table_head']),
                            ('TEXTCOLOR', (0, 0), (-1, 0), colors_theme['heading']),
                            ('ALIGN', (0, 0), (-1, 0), 'CENTER'),
                            ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
                            ('BOTTOMPADDING', (0, 0), (-1, 0), 12),
                            ('GRID', (0, 0), (-1, -1), 1, colors_theme['line']),
                            ('VALIGN', (0, 0), (-1, -1), 'MIDDLE'),
                            ('ALIGN', (1, 1), (1, -1), 'CENTER'),
                            ('ALIGN', (2, 1), (2, -1), 'CENTER'),
                        ]))
                        elements.append(table)
                
                # Add textual summary if available
                if isinstance(summary, dict) and 'overview' in summary:
                    elements.append(Spacer(1, 12))
                    elements.append(Paragraph(summary['overview'], styles['Normal']))
                elif isinstance(summary, str):
                    elements.append(Paragraph(summary, styles['Normal']))
                
                elements.append(Spacer(1, 24))
            
            # Add recommendations section
            if (self.include_recommendations and 
                ('recommendations' in data or 'warnings' in data or 'suggestions' in data)):
                elements.append(Paragraph("Recommendations", styles['Heading2']))
                
                # Process warnings
                if 'warnings' in data and data['warnings']:
                    elements.append(Paragraph("Issues to Fix", styles['Heading2']))
                    warnings = data['warnings']
                    if isinstance(warnings, list):
                        items = []
                        for warning in warnings:
                            if isinstance(warning, dict) and 'message' in warning:
                                items.append(ListItem(Paragraph(warning['message'], styles['Error'])))
                            elif isinstance(warning, str):
                                items.append(ListItem(Paragraph(warning, styles['Error'])))
                        
                        if items:
                            elements.append(ListFlowable(items, bulletType='bullet'))
                    
                    elements.append(Spacer(1, 12))
                
                # Process suggestions
                if 'suggestions' in data and data['suggestions']:
                    elements.append(Paragraph("Improvements", styles['Heading2']))
                    suggestions = data['suggestions']
                    if isinstance(suggestions, list):
                        items = []
                        for suggestion in suggestions:
                            if isinstance(suggestion, dict) and 'message' in suggestion:
                                items.append(ListItem(Paragraph(suggestion['message'], styles['Warning'])))
                            elif isinstance(suggestion, str):
                                items.append(ListItem(Paragraph(suggestion, styles['Warning'])))
                        
                        if items:
                            elements.append(ListFlowable(items, bulletType='bullet'))
                    
                    elements.append(Spacer(1, 12))
                
                # Process recommendations
                if 'recommendations' in data and data['recommendations']:
                    elements.append(Paragraph("Recommendations", styles['Heading2']))
                    recommendations = data['recommendations']
                    if isinstance(recommendations, list):
                        items = []
                        for rec in recommendations:
                            if isinstance(rec, dict) and 'message' in rec:
                                items.append(ListItem(Paragraph(rec['message'], styles['Normal'])))
                            elif isinstance(rec, str):
                                items.append(ListItem(Paragraph(rec, styles['Normal'])))
                        
                        if items:
                            elements.append(ListFlowable(items, bulletType='bullet'))
                
                elements.append(Spacer(1, 24))
            
            # Add detailed results section
            if self.include_details:
                elements.append(Paragraph("Detailed Results", styles['Heading2']))
                
                # Process each analyzer's results
                for analyzer_name, results in data.items():
                    # Skip non-analyzer data
                    if analyzer_name in ('url', 'summary', 'recommendations', 'warnings', 'suggestions'):
                        continue
                    
                    # Add analyzer section
                    elements.append(Paragraph(analyzer_name.replace('_', ' ').title(), styles['Heading2']))
                    
                    # Process dictionary results
                    if isinstance(results, dict):
                        for key, value in results.items():
                            # Skip complex nested structures, except for specific known ones
                            if isinstance(value, dict) and key in ('scores', 'metrics', 'statistics'):
                                elements.append(Paragraph(key.replace('_', ' ').title(), styles['Heading2']))
                                
                                # Create a table for the metrics
                                table_data = []
                                table_data.append(["Metric", "Value"])
                                
                                for metric_key, metric_value in value.items():
                                    if not isinstance(metric_value, (dict, list)):
                                        table_data.append([
                                            metric_key.replace('_', ' ').title(),
                                            str(metric_value)
                                        ])
                                
                                if len(table_data) > 1:
                                    table = Table(table_data, colWidths=[8*cm, 8*cm])
                                    table.setStyle(TableStyle([
                                        ('BACKGROUND', (0, 0), (-1, 0), colors_theme['table_head']),
                                        ('TEXTCOLOR', (0, 0), (-1, 0), colors_theme['heading']),
                                        ('ALIGN', (0, 0), (-1, 0), 'CENTER'),
                                        ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
                                        ('BOTTOMPADDING', (0, 0), (-1, 0), 12),
                                        ('GRID', (0, 0), (-1, -1), 1, colors_theme['line']),
                                        ('VALIGN', (0, 0), (-1, -1), 'MIDDLE'),
                                    ]))
                                    elements.append(table)
                                    elements.append(Spacer(1, 12))
                            elif not isinstance(value, (dict, list)):
                                elements.append(Paragraph(
                                    f"<b>{key.replace('_', ' ').title()}:</b> {value}",
                                    styles['Normal']
                                ))
                    
                    elements.append(Spacer(1, 12))
                
                elements.append(PageBreak())
            
            # Build the PDF document
            doc = SimpleDocTemplate(
                self.output_path, 
                pagesize=page_size,
                title=self.title,
                author="Summit SEO Tool",
                subject="SEO Analysis Report"
            )
            
            # Generate the PDF
            doc.build(elements)
            
            # Return information about the generated report
            return {
                'format': 'pdf',
                'file_path': self.output_path,
                'file_size': os.path.getsize(self.output_path),
                'title': self.title,
                'generated_at': datetime.now().isoformat()
            }
            
        except Exception as e:
            raise ReportGenerationError(f"PDF report generation failed: {str(e)}")

    def validate_config(self) -> None:
        """Validate the reporter configuration.
        
        Raises:
            ValueError: If configuration is invalid.
        """
        # Check output path
        if 'output_path' not in self.config:
            raise ValueError("output_path is required in configuration")
            
        # Validate page size if provided
        valid_page_sizes = ['A4', 'Letter', 'Legal']
        if 'page_size' in self.config and self.config['page_size'] not in valid_page_sizes:
            raise ValueError(f"page_size must be one of: {', '.join(valid_page_sizes)}")
            
        # Validate theme if provided
        valid_themes = ['default', 'light', 'dark']
        if 'theme' in self.config and self.config['theme'] not in valid_themes:
            raise ValueError(f"theme must be one of: {', '.join(valid_themes)}")
            
        # Check if logo path exists
        if 'logo_path' in self.config and not os.path.exists(self.config['logo_path']):
            raise ValueError(f"Logo file not found at {self.config['logo_path']}")

    async def generate_batch_report(self, data: List[Dict[str, Any]]) -> ReportResult:
        """Generate a batch report for multiple analysis results.
        
        Args:
            data: List of dictionaries containing analysis results.
        
        Returns:
            ReportResult containing the generated report and metadata.
        
        Raises:
            ReportGenerationError: If report generation fails.
        """
        if not data:
            raise ReportGenerationError("No data provided for batch report")
            
        try:
            # Import ReportLab libraries
            try:
                from reportlab.lib.pagesizes import A4, letter, legal
                from reportlab.lib import colors
                from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
                from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle, Image
                from reportlab.lib.units import inch
            except ImportError:
                raise ReportGenerationError("ReportLab library not installed. Please install with 'pip install reportlab'")
                
            # Set output path
            output_path = self.config['output_path']
            
            # Create document with appropriate page size
            page_size = self.config.get('page_size', 'A4')
            if page_size == 'A4':
                doc_page_size = A4
            elif page_size == 'Letter':
                doc_page_size = letter
            elif page_size == 'Legal':
                doc_page_size = legal
            else:
                doc_page_size = A4
                
            # Create the document
            doc = SimpleDocTemplate(
                output_path,
                pagesize=doc_page_size,
                title=self.config.get('title', 'Summit SEO Batch Analysis Report')
            )
            
            # Get styles
            styles = getSampleStyleSheet()
            title_style = styles['Title']
            heading1_style = styles['Heading1']
            heading2_style = styles['Heading2']
            normal_style = styles['Normal']
            
            # Build document content
            story = []
            
            # Title
            title = self.config.get('title', 'Summit SEO Analysis Report')
            story.append(Paragraph(title, title_style))
            story.append(Spacer(1, 0.25 * inch))
            
            # Add date
            date_str = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
            story.append(Paragraph(f"Generated on: {date_str}", normal_style))
            story.append(Spacer(1, 0.25 * inch))
            
            # Process each dataset
            for i, item in enumerate(data):
                site_url = item.get('url', f'Report #{i+1}')
                story.append(Paragraph(f"Report for: {site_url}", heading1_style))
                story.append(Spacer(1, 0.15 * inch))
                
                # Add summary if available
                if 'summary' in item and self.config.get('include_summary', True):
                    story.append(Paragraph("Summary", heading2_style))
                    
                    summary = item['summary']
                    if 'overview' in summary:
                        story.append(Paragraph(summary['overview'], normal_style))
                        
                    if 'score' in summary:
                        story.append(Paragraph(f"Overall Score: {summary['score']}/100", normal_style))
                        
                    # Add a spacer
                    story.append(Spacer(1, 0.15 * inch))
                
                # Add recommendations if available
                if 'recommendations' in item and self.config.get('include_recommendations', True):
                    story.append(Paragraph("Recommendations", heading2_style))
                    
                    for rec in item['recommendations']:
                        if isinstance(rec, str):
                            story.append(Paragraph(f"• {rec}", normal_style))
                        elif isinstance(rec, dict) and 'message' in rec:
                            story.append(Paragraph(f"• {rec['message']}", normal_style))
                            
                    # Add a spacer
                    story.append(Spacer(1, 0.15 * inch))
                
                # Add page break between reports (except for the last one)
                if i < len(data) - 1:
                    story.append(Paragraph("", normal_style))
                    story.append(Spacer(1, 0.5 * inch))
            
            # Build the PDF
            doc.build(story)
            
            # Create metadata
            metadata = self._create_metadata('pdf')
            
            # Create result object
            result = ReportResult(
                content=output_path,
                metadata=metadata,
                format='pdf'
            )
            
            return result
            
        except Exception as e:
            raise ReportGenerationError(f"PDF batch report generation failed: {str(e)}") 