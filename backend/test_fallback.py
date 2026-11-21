import sys
sys.path.insert(0, '.')
from src.data.samples import get_sample_catalog
print('Sample catalog loaded successfully')
print(f'Products: {len(get_sample_catalog().products)}')
print('Sample product list for serums:')
from src.services.market_research import GeminiMarketResearch
r = GeminiMarketResearch()
print('API key:', bool(r.api_key))
print('Model:', r.model)
