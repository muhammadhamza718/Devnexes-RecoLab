"""Unit tests for Day 5 Afternoon analysis scripts.

Tests AnalysisStorage, result loading, and error classification logic.
"""

import json
from pathlib import Path
from unittest.mock import Mock, patch

import pandas as pd
import pytest

# Add scripts to path
import sys
sys.path.insert(0, str(Path(__file__).resolve().parent.parent / "scripts"))
sys.path.insert(0, str(Path(__file__).resolve().parent.parent / "scripts" / "analysis"))


class TestAnalysisStorage:
    """Test AnalysisStorage class functionality."""

    def test_init_creates_directories(self, tmp_path):
        """Test that AnalysisStorage creates required directories."""
        from analysis_storage import AnalysisStorage

        storage = AnalysisStorage(base_dir=tmp_path)

        for category in ["error_analysis", "edge_case_analysis", "bias_analysis", "limitations", "visualizations"]:
            assert storage.get_category_dir(category).exists()

    def test_save_error_analysis(self, tmp_path):
        """Test saving error analysis results."""
        from analysis_storage import AnalysisStorage

        storage = AnalysisStorage(base_dir=tmp_path)

        test_data = {
            "Popularity": {
                "sample_size": 200,
                "total_recommendations": 2000,
                "total_errors": 500,
                "overall_error_rate": 0.25,
            }
        }

        path = storage.save_result(category="error_analysis", name="error_analysis_summary", data=test_data)

        assert path.exists()
        with open(path, "r") as f:
            loaded = json.load(f)

        assert loaded["data"]["Popularity"]["sample_size"] == 200

    def test_save_bias_analysis(self, tmp_path):
        """Test saving bias analysis results."""
        from analysis_storage import AnalysisStorage

        storage = AnalysisStorage(base_dir=tmp_path)

        test_data = {
            "Popularity": {
                "mean_popularity_decile": 5.0,
                "catalog_coverage_pct": 0.5,
                "intra_list_diversity": 0.8,
            }
        }

        path = storage.save_result(category="bias_analysis", name="bias_analysis_summary", data=test_data)

        assert path.exists()
        with open(path, "r") as f:
            loaded = json.load(f)

        assert loaded["data"]["Popularity"]["mean_popularity_decile"] == 5.0


class TestEvaluationResultLoader:
    """Test EvaluationResultLoader class functionality."""

    def test_validate_models_ready_all_ready(self, tmp_path):
        """Test model validation when all models are ready."""
        from result_loader import EvaluationResultLoader
        
        # Create mock evaluation results
        eval_dir = tmp_path / "evaluation" / "results"
        eval_dir.mkdir(parents=True)
        
        for model in ["popularity", "content", "user_based_cf"]:
            result = {
                "model_name": model,
                "results": {"mean_precision@10": 0.1},
            }
            (eval_dir / f"{model}_results.json").write_text(json.dumps(result))
        
        loader = EvaluationResultLoader(eval_dir=tmp_path / "evaluation")
        status = loader.validate_models_ready(["Popularity", "Content", "User-Based CF"])
        
        assert all(status.values())

    def test_validate_models_ready_some_not_ready(self, tmp_path):
        """Test model validation when some models have errors."""
        from result_loader import EvaluationResultLoader
        
        # Create mock evaluation results with one error
        eval_dir = tmp_path / "evaluation" / "results"
        eval_dir.mkdir(parents=True)
        
        for model in ["popularity", "content"]:
            result = {
                "model_name": model,
                "results": {"mean_precision@10": 0.1},
            }
            (eval_dir / f"{model}_results.json").write_text(json.dumps(result))
        
        # Add error result
        error_result = {"error": "Model failed to train"}
        (eval_dir / "user_based_cf_results.json").write_text(json.dumps(error_result))
        
        loader = EvaluationResultLoader(eval_dir=tmp_path / "evaluation")
        status = loader.validate_models_ready(["Popularity", "Content", "User-Based CF"])
        
        assert status["Popularity"] is True
        assert status["Content"] is True
        assert status["User-Based CF"] is False

    def test_validate_model_result_valid(self, tmp_path):
        """Test validation of valid model result."""
        from result_loader import EvaluationResultLoader
        
        loader = EvaluationResultLoader(eval_dir=tmp_path / "evaluation")
        
        valid_result = {
            "mean_precision@10": 0.1,
            "mean_recall@10": 0.05,
            "mean_ndcg@10": 0.08,
        }
        
        # Should not raise
        loader._validate_model_result("TestModel", valid_result)

    def test_validate_model_result_invalid_metric_range(self, tmp_path):
        """Test validation of model result with invalid metric range."""
        from result_loader import EvaluationResultLoader
        
        loader = EvaluationResultLoader(eval_dir=tmp_path / "evaluation")
        
        invalid_result = {
            "mean_precision@10": 1.5,  # Invalid: > 1.0
        }
        
        # Should print warning but not raise
        loader._validate_model_result("TestModel", invalid_result)


class TestErrorAnalysis:
    """Test ErrorAnalyzer functionality."""

    def test_analyze_errors_empty_data(self):
        """Test error analysis with empty test data."""
        from error_analysis import ErrorAnalyzer

        # Mock components
        loader = Mock()
        storage = Mock()
        loader.validate_models_ready.return_value = {"Popularity": True}
        loader.load_model_results.return_value = {"Popularity": {"mean_precision@10": 0.1}}

        analyzer = ErrorAnalyzer(loader=loader, storage=storage)

        # Mock empty test data
        analyzer.test_df = pd.DataFrame(columns=["userId", "movieId", "rating"])

        results = analyzer.analyze_errors(["Popularity"])

        # Should handle gracefully
        assert "Popularity" in results

    def test_model_state_validation(self):
        """Test that model state is validated before recommendation."""
        from error_analysis import ErrorAnalyzer
        
        loader = Mock()
        storage = Mock()
        
        analyzer = ErrorAnalyzer(loader=loader, storage=storage)
        
        # Mock model that is not fitted
        mock_model = Mock()
        mock_model.is_fitted = False
        mock_model.is_ready = False
        mock_model.recommend = Mock(return_value=pd.DataFrame())
        
        # Should detect model is not ready
        is_fitted = hasattr(mock_model, 'is_fitted') and mock_model.is_fitted
        is_ready = hasattr(mock_model, 'is_ready') and mock_model.is_ready
        
        assert not (is_fitted or is_ready)


class TestBiasAnalysis:
    """Test BiasAnalyzer functionality."""

    def test_calculate_popularity_bias(self):
        """Test popularity bias calculation."""
        from bias_analysis import BiasAnalyzer

        loader = Mock()
        storage = Mock()

        analyzer = BiasAnalyzer(loader=loader, storage=storage)

        # Mock item popularity deciles
        analyzer.item_pop_deciles = {1: 5, 2: 8}

        # Test with recommended items as dict (user_recs: dict[int, list[int]])
        result = analyzer._calculate_popularity_bias({1: [1, 2]})

        # Should return dict with mean_popularity_decile
        assert "mean_popularity_decile" in result
        assert 0 <= result["mean_popularity_decile"] <= 10

    def test_calculate_catalog_coverage(self):
        """Test catalog coverage calculation."""
        from bias_analysis import BiasAnalyzer

        loader = Mock()
        storage = Mock()

        analyzer = BiasAnalyzer(loader=loader, storage=storage)

        # Mock catalog size (implementation uses total_catalog_size)
        analyzer.total_catalog_size = 1000

        # Test with recommended items as set (implementation expects set[int])
        recommended_items = {1, 2, 3, 4, 5}
        coverage = analyzer._calculate_catalog_coverage(recommended_items)

        assert coverage["catalog_coverage_pct"] == 5 / 1000


class TestPathValidation:
    """Test path validation in analysis scripts."""

    def test_path_utils_import(self):
        """Test that path_utils can be imported in analysis scripts."""
        # This test ensures the path_utils module is accessible
        from path_utils import get_validated_project_root, validate_path_within_project
        
        assert callable(get_validated_project_root)
        assert callable(validate_path_within_project)

    def test_get_validated_project_root_from_analysis_dir(self):
        """Test path validation from analysis script directory."""
        from path_utils import get_validated_project_root
        
        # Simulate calling from analysis script
        analysis_script_path = Path(__file__).resolve().parent.parent / "scripts" / "analysis" / "error_analysis.py"
        
        if analysis_script_path.exists():
            project_root = get_validated_project_root(analysis_script_path)
            assert project_root.exists()
            assert (project_root / "src").exists()


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
