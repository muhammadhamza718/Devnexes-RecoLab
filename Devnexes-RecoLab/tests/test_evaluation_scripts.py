"""Unit tests for Day 5 Morning evaluation scripts.

Tests ResultStorage, Validation functions, and metric calculation accuracy.
"""

import json
from pathlib import Path
from unittest.mock import Mock, patch

import pandas as pd
import pytest

# Add scripts to path
import sys
sys.path.insert(0, str(Path(__file__).resolve().parent.parent / "scripts"))
sys.path.insert(0, str(Path(__file__).resolve().parent.parent / "scripts" / "evaluation"))


class TestResultStorage:
    """Test ResultStorage class functionality."""

    def test_init_creates_directories(self, tmp_path):
        """Test that ResultStorage creates required directories."""
        from result_storage import ResultStorage
        
        storage = ResultStorage(base_dir=tmp_path)
        
        assert storage.results_dir.exists()
        assert storage.comparison_dir.exists()
        assert storage.segmented_dir.exists()
        assert storage.visualizations_dir.exists()

    def test_save_model_results(self, tmp_path):
        """Test saving model evaluation results."""
        from result_storage import ResultStorage
        
        storage = ResultStorage(base_dir=tmp_path)
        
        test_results = {
            "mean_precision@5": 0.1,
            "mean_recall@5": 0.05,
            "mean_ndcg@5": 0.08,
            "catalog_coverage": 0.5,
        }
        
        path = storage.save_model_results("TestModel", test_results)
        
        assert path.exists()
        with open(path, "r") as f:
            loaded = json.load(f)
        
        assert loaded["model_name"] == "TestModel"
        assert loaded["results"]["mean_precision@5"] == 0.1

    def test_save_segmented_results(self, tmp_path):
        """Test saving segmented evaluation results."""
        from result_storage import ResultStorage
        
        storage = ResultStorage(base_dir=tmp_path)
        
        test_segment_data = {
            "mean_precision@10": 0.15,
            "mean_recall@10": 0.1,
            "n_test_users": 100,
        }
        
        path = storage.save_segmented_results("TestModel", "cold_start_users", test_segment_data)
        
        assert path.exists()
        with open(path, "r") as f:
            loaded = json.load(f)
        
        assert loaded["model_name"] == "TestModel"
        assert loaded["segment_name"] == "cold_start_users"


class TestValidation:
    """Test validation functions."""

    def test_validate_train_data_valid(self, tmp_path):
        """Test validation of valid training data."""
        from validation import validate_train_data
        
        # Create valid train.csv
        train_df = pd.DataFrame({
            "userId": [1, 2, 3],
            "movieId": [1, 2, 3],
            "rating": [4.0, 5.0, 3.0],
            "timestamp": [1000, 2000, 3000],
        })
        train_path = tmp_path / "train.csv"
        train_df.to_csv(train_path, index=False)
        
        # Should not raise
        validate_train_data(train_path)

    def test_validate_train_data_missing_columns(self, tmp_path):
        """Test validation fails with missing columns."""
        from validation import validate_train_data, ValidationError
        
        # Create invalid train.csv (missing timestamp)
        train_df = pd.DataFrame({
            "userId": [1, 2, 3],
            "movieId": [1, 2, 3],
            "rating": [4.0, 5.0, 3.0],
        })
        train_path = tmp_path / "train.csv"
        train_df.to_csv(train_path, index=False)
        
        with pytest.raises(ValidationError):
            validate_train_data(train_path)

    def test_validate_movies_data_valid(self, tmp_path):
        """Test validation of valid movies data."""
        from validation import validate_movies_data
        
        # Create valid movies.csv
        movies_df = pd.DataFrame({
            "movieId": [1, 2, 3],
            "title": ["Movie1", "Movie2", "Movie3"],
            "genres": ["Action|Drama", "Comedy", "Horror"],
        })
        movies_path = tmp_path / "movies.csv"
        movies_df.to_csv(movies_path, index=False)
        
        # Should not raise
        validate_movies_data(movies_path)


class TestStatisticalAnalysis:
    """Test statistical analysis functions."""

    def test_compare_models_ranks_correctly(self):
        """Test that model comparison produces correct rankings."""
        from statistical_analysis import StatisticalAnalysis
        
        # Mock storage
        storage = Mock()
        storage.comparison_dir = Path("/tmp")
        
        analysis = StatisticalAnalysis(storage=storage)
        
        test_results = {
            "ModelA": {"mean_precision@10": 0.1, "mean_recall@10": 0.05, "mean_ndcg@10": 0.08},
            "ModelB": {"mean_precision@10": 0.2, "mean_recall@10": 0.1, "mean_ndcg@10": 0.15},
        }
        
        rankings = analysis._rank_models(test_results)
        
        assert rankings["mean_precision@10"][0] == "ModelB"
        assert rankings["mean_precision@10"][-1] == "ModelA"

    def test_significance_test_performs_t_test(self):
        """Test that significance testing performs actual statistical tests."""
        from statistical_analysis import StatisticalAnalysis
        
        storage = Mock()
        storage.comparison_dir = Path("/tmp")
        
        analysis = StatisticalAnalysis(storage=storage)
        
        test_results = {
            "ModelA": {"mean_precision@10": 0.1, "mean_recall@10": 0.05, "mean_ndcg@10": 0.08, "n_users": 100},
            "ModelB": {"mean_precision@10": 0.2, "mean_recall@10": 0.1, "mean_ndcg@10": 0.15, "n_users": 100},
        }
        
        tests = analysis._perform_significance_tests(test_results)
        
        assert "comparisons" in tests
        assert len(tests["comparisons"]) > 0
        assert "t_statistic" in tests["comparisons"][0]
        assert "p_value" in tests["comparisons"][0]


class TestPathUtils:
    """Test path validation utilities."""

    def test_get_validated_project_root_valid(self):
        """Test that get_validated_project_root returns valid path."""
        from path_utils import get_validated_project_root
        
        # Test with current project structure
        project_root = get_validated_project_root()
        
        assert project_root.exists()
        assert (project_root / "src").exists()
        assert (project_root / "data").exists()
        assert (project_root / "scripts").exists()
        assert (project_root / "ui").exists()

    def test_validate_path_within_project_valid(self):
        """Test path validation within project."""
        from path_utils import validate_path_within_project
        
        project_root = Path(__file__).resolve().parent.parent.parent
        valid_path = project_root / "src"
        
        assert validate_path_within_project(valid_path, project_root) is True

    def test_validate_path_within_project_invalid(self):
        """Test path validation rejects paths outside project."""
        from path_utils import validate_path_within_project
        
        project_root = Path(__file__).resolve().parent.parent.parent
        invalid_path = Path("C:\\Windows")
        
        assert validate_path_within_project(invalid_path, project_root) is False


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
