import pytest
from typing import Dict, Any
from summit_seo.processor import (
    BaseProcessor,
    ProcessorFactory,
    ProcessedData,
    ProcessingError
)

# Mock processor for testing
class MockProcessor(BaseProcessor[str, int]):
    async def process(self, data: str) -> ProcessedData[str, int]:
        await self.validate_input(data)
        processed = len(data)  # Simple processing: string length
        await self.validate_output(processed)
        return ProcessedData(
            input_data=data,
            output_data=processed,
            metadata={"test": "value"}
        )

@pytest.fixture
def config():
    return {"test_config": "value"}

class TestBaseProcessor:
    def test_init(self):
        processor = MockProcessor()
        assert processor.config == {}
        
        processor_with_config = MockProcessor({"key": "value"})
        assert processor_with_config.config == {"key": "value"}
    
    @pytest.mark.asyncio
    async def test_validate_input(self):
        processor = MockProcessor()
        
        # Should raise error for None input
        with pytest.raises(ProcessingError):
            await processor.validate_input(None)
        
        # Should not raise error for valid input
        await processor.validate_input("test")
    
    @pytest.mark.asyncio
    async def test_validate_output(self):
        processor = MockProcessor()
        
        # Should raise error for None output
        with pytest.raises(ProcessingError):
            await processor.validate_output(None)
        
        # Should not raise error for valid output
        await processor.validate_output(42)
    
    @pytest.mark.asyncio
    async def test_process(self):
        processor = MockProcessor()
        
        data = await processor.process("test")
        assert isinstance(data, ProcessedData)
        assert data.input_data == "test"
        assert data.output_data == 4  # Length of "test"
        assert data.metadata == {"test": "value"}
    
    @pytest.mark.asyncio
    async def test_preprocess(self):
        processor = MockProcessor()
        
        data = "test"
        processed = await processor.preprocess(data)
        assert processed == data  # Default implementation returns input unchanged
    
    @pytest.mark.asyncio
    async def test_postprocess(self):
        processor = MockProcessor()
        
        data = 42
        processed = await processor.postprocess(data)
        assert processed == data  # Default implementation returns input unchanged

class TestProcessorFactory:
    def setup_method(self):
        ProcessorFactory.clear_registry()
    
    def test_register(self):
        ProcessorFactory.register("mock", MockProcessor)
        assert "mock" in ProcessorFactory.list_processors()
        
        # Test duplicate registration
        with pytest.raises(ValueError):
            ProcessorFactory.register("mock", MockProcessor)
        
        # Test invalid processor class
        class InvalidProcessor:
            pass
        
        with pytest.raises(ValueError):
            ProcessorFactory.register("invalid", InvalidProcessor)
    
    def test_create(self):
        ProcessorFactory.register("mock", MockProcessor)
        
        # Test creation without config
        processor = ProcessorFactory.create("mock")
        assert isinstance(processor, MockProcessor)
        assert processor.config == {}
        
        # Test creation with config
        config = {"test": "value"}
        processor = ProcessorFactory.create("mock", config)
        assert isinstance(processor, MockProcessor)
        assert processor.config == config
        
        # Test creation of unregistered processor
        with pytest.raises(ValueError):
            ProcessorFactory.create("nonexistent")
    
    def test_list_processors(self):
        assert ProcessorFactory.list_processors() == []
        
        ProcessorFactory.register("mock1", MockProcessor)
        ProcessorFactory.register("mock2", MockProcessor)
        
        processors = ProcessorFactory.list_processors()
        assert len(processors) == 2
        assert "mock1" in processors
        assert "mock2" in processors 