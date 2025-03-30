"""Test cases for base processor functionality."""

import pytest
from typing import Dict, Any
from datetime import datetime
from summit_seo.processor.base import (
    BaseProcessor,
    ProcessingResult,
    ValidationError,
    TransformationError
)

async def test_processor_initialization(mock_processor, sample_config):
    """Test processor initialization with configuration."""
    processor = mock_processor.__class__(sample_config)
    assert processor.config == sample_config
    assert processor.processed_count == 0
    assert processor.error_count == 0

async def test_processor_name(mock_processor):
    """Test processor name property."""
    assert mock_processor.name == 'MockProcessor'

async def test_validate_config_batch_size(sample_config):
    """Test batch size configuration validation."""
    # Valid batch size
    processor = MockProcessor(sample_config)
    assert processor.config['batch_size'] == 10
    
    # Invalid batch sizes
    invalid_batch_sizes = [0, -1, 'invalid']
    for batch_size in invalid_batch_sizes:
        with pytest.raises(ValidationError):
            MockProcessor({'batch_size': batch_size})

async def test_validate_config_max_retries(sample_config):
    """Test max retries configuration validation."""
    # Valid max retries
    processor = MockProcessor(sample_config)
    assert processor.config['max_retries'] == 3
    
    # Invalid max retries
    invalid_max_retries = [-1, 'invalid']
    for max_retries in invalid_max_retries:
        with pytest.raises(ValidationError):
            MockProcessor({'max_retries': max_retries})

async def test_process_valid_data(mock_processor, sample_data):
    """Test processing valid data."""
    result = await mock_processor.process(sample_data, sample_data['url'])
    
    assert isinstance(result, ProcessingResult)
    assert result.url == sample_data['url']
    assert result.processed_data == {'processed_' + k: v for k, v in sample_data.items()}
    assert result.processing_time > 0
    assert isinstance(result.timestamp, datetime)
    assert not result.errors
    assert not result.warnings
    assert mock_processor.processed_count == 1
    assert mock_processor.error_count == 0

async def test_process_invalid_data(mock_processor):
    """Test processing invalid data."""
    invalid_data = {'invalid_field': 'value'}
    result = await mock_processor.process(invalid_data, 'https://example.com')
    
    assert isinstance(result, ProcessingResult)
    assert not result.processed_data
    assert len(result.errors) == 1
    assert 'Validation error' in result.errors[0]
    assert mock_processor.processed_count == 0
    assert mock_processor.error_count == 1

async def test_process_batch(mock_processor, sample_batch_data):
    """Test batch processing."""
    urls = [data['url'] for data in sample_batch_data]
    results = await mock_processor.process_batch(list(zip(sample_batch_data, urls)))
    
    assert len(results) == len(sample_batch_data)
    for result in results:
        assert isinstance(result, ProcessingResult)
        assert not result.errors
        assert not result.warnings
    
    assert mock_processor.processed_count == len(sample_batch_data)
    assert mock_processor.error_count == 0

async def test_process_batch_with_errors(mock_processor, sample_batch_data):
    """Test batch processing with some invalid data."""
    # Corrupt some data
    sample_batch_data[2] = {'invalid_field': 'value'}
    
    urls = [data.get('url', 'https://example.com') for data in sample_batch_data]
    results = await mock_processor.process_batch(list(zip(sample_batch_data, urls)))
    
    assert len(results) == len(sample_batch_data)
    assert any(result.errors for result in results)
    assert mock_processor.error_count > 0

async def test_validate_input_type(mock_processor):
    """Test input data type validation."""
    invalid_inputs = [
        None,
        'string',
        123,
        [],
        set()
    ]
    
    for invalid_input in invalid_inputs:
        with pytest.raises(ValidationError):
            mock_processor._validate_input(invalid_input)

async def test_validate_output_type(mock_processor):
    """Test output data type validation."""
    invalid_outputs = [
        None,
        'string',
        123,
        [],
        set()
    ]
    
    for invalid_output in invalid_outputs:
        with pytest.raises(ValidationError):
            mock_processor._validate_output(invalid_output)

async def test_get_metadata(mock_processor, sample_config):
    """Test metadata collection."""
    processor = mock_processor.__class__(sample_config)
    metadata = processor._get_metadata()
    
    assert metadata['processor_name'] == processor.name
    assert metadata['processed_count'] == processor.processed_count
    assert metadata['error_count'] == processor.error_count
    assert metadata['config'] == sample_config

async def test_required_fields_implementation(mock_processor):
    """Test required fields implementation."""
    required_fields = mock_processor._get_required_fields()
    assert isinstance(required_fields, list)
    assert 'test_field' in required_fields

async def test_process_data_implementation(mock_processor, sample_data):
    """Test process data implementation."""
    processed_data = await mock_processor._process_data(sample_data)
    assert isinstance(processed_data, dict)
    assert all(k.startswith('processed_') for k in processed_data.keys())

async def test_concurrent_processing(mock_processor, sample_batch_data):
    """Test concurrent processing of multiple items."""
    import asyncio
    
    urls = [data['url'] for data in sample_batch_data]
    tasks = [
        mock_processor.process(data, url)
        for data, url in zip(sample_batch_data, urls)
    ]
    
    results = await asyncio.gather(*tasks)
    
    assert len(results) == len(sample_batch_data)
    assert all(isinstance(r, ProcessingResult) for r in results)
    assert mock_processor.processed_count == len(sample_batch_data)

async def test_error_handling_inheritance(mock_processor, sample_data):
    """Test proper error handling inheritance."""
    class ErrorProcessor(mock_processor.__class__):
        async def _process_data(self, data: Dict[str, Any]) -> Dict[str, Any]:
            raise TransformationError("Test error")
    
    processor = ErrorProcessor()
    result = await processor.process(sample_data, sample_data['url'])
    
    assert result.errors
    assert 'Transformation error' in result.errors[0]
    assert processor.error_count == 1

async def test_processing_metrics(mock_processor, sample_data):
    """Test processing metrics tracking."""
    # Process valid data
    await mock_processor.process(sample_data, sample_data['url'])
    assert mock_processor.processed_count == 1
    assert mock_processor.error_count == 0
    
    # Process invalid data
    await mock_processor.process({'invalid': 'data'}, 'https://example.com')
    assert mock_processor.processed_count == 1
    assert mock_processor.error_count == 1 