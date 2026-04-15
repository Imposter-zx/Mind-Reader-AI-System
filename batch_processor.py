#!/usr/bin/env python3
"""
Mind Reader AI System - Batch Processing Script
Process large volumes of text efficiently with reporting
"""

import json
import csv
import time
from datetime import datetime
from pathlib import Path
from mind_reader_lightweight import MindScoreAPI


class BatchProcessor:
    """Batch processing engine for large-scale analysis"""
    
    def __init__(self):
        self.api = MindScoreAPI()
        self.results = []
        self.processing_time = 0
    
    def process_from_file(self, filepath: str, output_format: str = 'json') -> dict:
        """
        Process texts from file
        
        Supports: .txt (one text per line), .json (array of strings), .csv (text column)
        """
        filepath = Path(filepath)
        
        if not filepath.exists():
            return {
                'status': 'error',
                'message': f'File not found: {filepath}'
            }
        
        # Read texts
        texts = self._read_file(filepath)
        
        if not texts:
            return {
                'status': 'error',
                'message': 'No valid texts found in file'
            }
        
        # Process texts
        return self.process_batch(texts, output_format)
    
    def _read_file(self, filepath: Path) -> list:
        """Read texts from file based on extension"""
        texts = []
        
        try:
            if filepath.suffix == '.txt':
                with open(filepath, 'r', encoding='utf-8') as f:
                    texts = [line.strip() for line in f if line.strip()]
            
            elif filepath.suffix == '.json':
                with open(filepath, 'r', encoding='utf-8') as f:
                    data = json.load(f)
                    if isinstance(data, list):
                        texts = [str(t) for t in data if t]
                    elif isinstance(data, dict) and 'texts' in data:
                        texts = [str(t) for t in data['texts'] if t]
            
            elif filepath.suffix == '.csv':
                with open(filepath, 'r', encoding='utf-8') as f:
                    reader = csv.DictReader(f)
                    # Try to find text column
                    for row in reader:
                        for key in ['text', 'Text', 'content', 'Content', 'message', 'Message']:
                            if key in row:
                                texts.append(row[key].strip())
                                break
                        else:
                            # If no specific column, take first value
                            texts.append(str(list(row.values())[0]).strip())
            
            else:
                print(f"Unsupported file format: {filepath.suffix}")
        
        except Exception as e:
            print(f"Error reading file: {str(e)}")
        
        return texts
    
    def process_batch(self, texts: list, output_format: str = 'json') -> dict:
        """Process a batch of texts"""
        print(f"\n{'='*80}")
        print(f"BATCH PROCESSING: {len(texts)} texts")
        print(f"{'='*80}\n")
        
        start_time = time.time()
        self.results = []
        
        for i, text in enumerate(texts, 1):
            # Progress indicator
            if i % max(1, len(texts) // 10) == 0 or i == 1:
                progress = (i / len(texts)) * 100
                print(f"Progress: {progress:.0f}% ({i}/{len(texts)})")
            
            try:
                result = self.api.analyze(text, detailed=False)
                self.results.append({
                    'index': i,
                    'text': text[:100],  # Store first 100 chars
                    'result': result
                })
            
            except Exception as e:
                self.results.append({
                    'index': i,
                    'text': text[:100],
                    'error': str(e)
                })
        
        self.processing_time = time.time() - start_time
        
        # Return summary
        return self._generate_summary(output_format)
    
    def _generate_summary(self, output_format: str = 'json') -> dict:
        """Generate processing summary"""
        successful = [r for r in self.results if 'result' in r]
        failed = [r for r in self.results if 'error' in r]
        
        emotions = {}
        mind_scores = []
        
        for result in successful:
            emotion = result['result']['emotion_analysis']['emotion']
            emotions[emotion] = emotions.get(emotion, 0) + 1
            mind_scores.append(result['result']['mind_score']['overall_score'])
        
        summary = {
            'status': 'success',
            'total_processed': len(self.results),
            'successful': len(successful),
            'failed': len(failed),
            'processing_time_seconds': round(self.processing_time, 2),
            'texts_per_second': round(len(successful) / max(1, self.processing_time), 2),
            'statistics': {
                'emotion_distribution': emotions,
                'average_mind_score': round(sum(mind_scores) / len(mind_scores), 2) if mind_scores else 0,
                'min_score': round(min(mind_scores), 2) if mind_scores else 0,
                'max_score': round(max(mind_scores), 2) if mind_scores else 0
            },
            'detailed_results': successful[:10]  # First 10 results
        }
        
        return summary
    
    def save_results(self, filepath: str = None) -> str:
        """Save results to file"""
        if filepath is None:
            timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
            filepath = f'batch_results_{timestamp}.json'
        
        filepath = Path(filepath)
        
        # Prepare data for JSON serialization
        export_data = {
            'timestamp': datetime.now().isoformat(),
            'total_analyses': len(self.results),
            'processing_time': self.processing_time,
            'results': []
        }
        
        for result in self.results:
            export_data['results'].append({
                'index': result['index'],
                'text': result['text'],
                'emotion': result['result'].get('emotion_analysis', {}).get('emotion', 'N/A') if 'result' in result else 'ERROR',
                'mind_score': result['result'].get('mind_score', {}).get('overall_score', 0) if 'result' in result else 0,
                'error': result.get('error', None)
            })
        
        try:
            with open(filepath, 'w', encoding='utf-8') as f:
                json.dump(export_data, f, indent=2)
            
            return f"✅ Results saved to: {filepath}"
        
        except Exception as e:
            return f"❌ Error saving results: {str(e)}"
    
    def generate_report(self) -> str:
        """Generate comprehensive report"""
        if not self.results:
            return "No results to report"
        
        successful = [r for r in self.results if 'result' in r]
        failed = [r for r in self.results if 'error' in r]
        
        emotions = {}
        mind_scores = []
        
        for result in successful:
            emotion = result['result']['emotion_analysis']['emotion']
            emotions[emotion] = emotions.get(emotion, 0) + 1
            mind_scores.append(result['result']['mind_score']['overall_score'])
        
        report = f"""
╔════════════════════════════════════════════════════════════════════════════╗
║              BATCH PROCESSING ANALYSIS REPORT                             ║
╚════════════════════════════════════════════════════════════════════════════╝

📊 PROCESSING METRICS:
  Total Texts Processed:   {len(self.results)}
  Successful Analyses:     {len(successful)}
  Failed Analyses:         {len(failed)}
  Processing Time:         {self.processing_time:.2f} seconds
  Texts per Second:        {len(successful) / max(1, self.processing_time):.2f}
  Average Time per Text:   {(self.processing_time / len(self.results) * 1000):.2f}ms

😊 EMOTION DISTRIBUTION:
"""
        
        for emotion, count in sorted(emotions.items(), key=lambda x: x[1], reverse=True):
            percentage = (count / len(successful)) * 100 if successful else 0
            bar = "█" * int(percentage / 5)
            report += f"  {emotion.capitalize():.<15} {bar:<20} {percentage:>5.1f}% ({count})\n"
        
        report += f"""

🧠 MIND SCORE ANALYSIS:
  Average Score:           {sum(mind_scores) / len(mind_scores) if mind_scores else 0:.2f}/100
  Highest Score:           {max(mind_scores) if mind_scores else 0:.2f}/100
  Lowest Score:            {min(mind_scores) if mind_scores else 0:.2f}/100

📈 PERFORMANCE ANALYSIS:
  System Status:           ✅ OPERATIONAL
  Processing Efficiency:   {(len(successful) / len(self.results) * 100):.1f}%
  Error Rate:              {(len(failed) / len(self.results) * 100):.1f}%

✨ SUMMARY:
  The batch processing successfully analyzed {len(successful)} texts
  with {(sum(mind_scores) / len(mind_scores) if mind_scores else 0):.0f} average mind score.
  Processing completed in {self.processing_time:.2f} seconds.
  
  Most detected emotion: {max(emotions, key=emotions.get) if emotions else 'N/A'}
  Analysis rate: {len(successful) / max(1, self.processing_time):.1f} texts/second

╚════════════════════════════════════════════════════════════════════════════╝
"""
        
        return report


def main():
    """Main execution"""
    import sys
    
    processor = BatchProcessor()
    
    print("\n" + "="*80)
    print("🧠 MIND READER AI SYSTEM - BATCH PROCESSOR")
    print("="*80 + "\n")
    
    # Check command line arguments
    if len(sys.argv) > 1:
        input_file = sys.argv[1]
        
        # Process file
        result = processor.process_from_file(input_file)
        
        if result['status'] == 'success':
            print(processor.generate_report())
            
            # Save results
            output_file = sys.argv[2] if len(sys.argv) > 2 else None
            print(processor.save_results(output_file))
        else:
            print(f"❌ {result['message']}")
    
    else:
        # Interactive mode
        print("📋 BATCH PROCESSING MODE\n")
        
        while True:
            filepath = input("Enter file path (or 'quit' to exit):\n→ ").strip()
            
            if filepath.lower() in ['quit', 'exit', 'q']:
                break
            
            # Process file
            result = processor.process_from_file(filepath)
            
            if result['status'] == 'success':
                print(processor.generate_report())
                
                # Ask to save
                save = input("\nSave results? (yes/no): ").strip().lower()
                if save in ['yes', 'y']:
                    output = input("Enter output filename (or press Enter for default): ").strip()
                    print(processor.save_results(output if output else None))
            else:
                print(f"❌ Error: {result['message']}\n")


if __name__ == '__main__':
    main()
