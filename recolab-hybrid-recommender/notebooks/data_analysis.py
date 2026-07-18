"""
Data Analysis Script for MovieLens Dataset
Following data-scientist agent standards for exploratory data analysis
"""

import pandas as pd
import numpy as np
import matplotlib
matplotlib.use('Agg')  # Use non-interactive backend
import matplotlib.pyplot as plt
import seaborn as sns
from pathlib import Path

# Set reproducibility seed per data-scientist standards
np.random.seed(42)

# Configure plotting
sns.set_style("whitegrid")
plt.rcParams['figure.figsize'] = (12, 8)
plt.rcParams['font.size'] = 10

def load_data(data_path: Path) -> tuple[pd.DataFrame, pd.DataFrame]:
    """Load MovieLens ratings and movies datasets."""
    ratings_path = data_path / "ml-latest-small" / "ratings.csv"
    movies_path = data_path / "ml-latest-small" / "movies.csv"
    
    ratings = pd.read_csv(ratings_path)
    movies = pd.read_csv(movies_path)
    
    return ratings, movies

def validate_data_structure(ratings: pd.DataFrame, movies: pd.DataFrame) -> None:
    """Validate data structure and quality per data-scientist standards."""
    print("=== Data Structure Validation ===")
    
    # Check ratings structure
    print(f"\nRatings Shape: {ratings.shape}")
    print(f"Ratings Columns: {ratings.columns.tolist()}")
    print(f"Ratings Data Types:\n{ratings.dtypes}")
    
    # Check movies structure
    print(f"\nMovies Shape: {movies.shape}")
    print(f"Movies Columns: {movies.columns.tolist()}")
    print(f"Movies Data Types:\n{movies.dtypes}")
    
    # Check for missing values
    print(f"\nRatings Missing Values:\n{ratings.isnull().sum()}")
    print(f"\nMovies Missing Values:\n{movies.isnull().sum()}")
    
    # Check for duplicates
    print(f"\nRatings Duplicates: {ratings.duplicated().sum()}")
    print(f"Movies Duplicates: {movies.duplicated().sum()}")
    
    # Basic statistics
    print(f"\nRatings Statistics:\n{ratings.describe()}")
    print(f"\nRating Distribution:\n{ratings['rating'].value_counts().sort_index()}")

def analyze_sparsity(ratings: pd.DataFrame) -> dict:
    """Analyze sparsity of the user-item matrix."""
    print("\n=== Sparsity Analysis ===")
    
    n_users = ratings['userId'].nunique()
    n_items = ratings['movieId'].nunique()
    n_ratings = len(ratings)
    
    # Calculate sparsity
    total_possible = n_users * n_items
    sparsity = 1.0 - (n_ratings / total_possible)
    
    print(f"Number of Users: {n_users}")
    print(f"Number of Movies: {n_items}")
    print(f"Number of Ratings: {n_ratings}")
    print(f"Total Possible Ratings: {total_possible}")
    print(f"Sparsity: {sparsity:.4f} ({sparsity * 100:.2f}%)")
    
    # User activity distribution
    user_activity = ratings.groupby('userId').size()
    print(f"\nUser Activity Statistics:")
    print(f"Mean ratings per user: {user_activity.mean():.2f}")
    print(f"Median ratings per user: {user_activity.median():.2f}")
    print(f"Min ratings per user: {user_activity.min()}")
    print(f"Max ratings per user: {user_activity.max()}")
    
    # Item popularity distribution
    item_popularity = ratings.groupby('movieId').size()
    print(f"\nItem Popularity Statistics:")
    print(f"Mean ratings per movie: {item_popularity.mean():.2f}")
    print(f"Median ratings per movie: {item_popularity.median():.2f}")
    print(f"Min ratings per movie: {item_popularity.min()}")
    print(f"Max ratings per movie: {item_popularity.max()}")
    
    # Cold start analysis
    cold_users = (user_activity <= 5).sum()
    cold_items = (item_popularity <= 5).sum()
    
    print(f"\nCold Start Analysis:")
    print(f"Users with <=5 ratings: {cold_users} ({cold_users/n_users*100:.2f}%)")
    print(f"Movies with <=5 ratings: {cold_items} ({cold_items/n_items*100:.2f}%)")
    
    return {
        'n_users': n_users,
        'n_items': n_items,
        'n_ratings': n_ratings,
        'sparsity': sparsity,
        'user_activity_mean': user_activity.mean(),
        'user_activity_median': user_activity.median(),
        'item_popularity_mean': item_popularity.mean(),
        'item_popularity_median': item_popularity.median(),
        'cold_users': cold_users,
        'cold_items': cold_items
    }

def visualize_distributions(ratings: pd.DataFrame, output_path: Path) -> None:
    """Create visualizations of data distributions."""
    print("\n=== Creating Visualizations ===")
    
    # Rating distribution
    plt.figure(figsize=(10, 6))
    ratings['rating'].value_counts().sort_index().plot(kind='bar')
    plt.title('Rating Distribution')
    plt.xlabel('Rating')
    plt.ylabel('Count')
    plt.tight_layout()
    plt.savefig(output_path / 'rating_distribution.png', dpi=300, bbox_inches='tight')
    plt.close()
    
    # User activity distribution
    plt.figure(figsize=(10, 6))
    user_activity = ratings.groupby('userId').size()
    plt.hist(user_activity, bins=50, edgecolor='black')
    plt.title('User Activity Distribution')
    plt.xlabel('Number of Ratings per User')
    plt.ylabel('Count')
    plt.tight_layout()
    plt.savefig(output_path / 'user_activity_distribution.png', dpi=300, bbox_inches='tight')
    plt.close()
    
    # Item popularity distribution
    plt.figure(figsize=(10, 6))
    item_popularity = ratings.groupby('movieId').size()
    plt.hist(item_popularity, bins=50, edgecolor='black')
    plt.title('Item Popularity Distribution')
    plt.xlabel('Number of Ratings per Movie')
    plt.ylabel('Count')
    plt.tight_layout()
    plt.savefig(output_path / 'item_popularity_distribution.png', dpi=300, bbox_inches='tight')
    plt.close()
    
    print("Visualizations saved successfully")

def main():
    """Main data analysis workflow."""
    # Setup paths
    project_root = Path(__file__).parent.parent
    data_path = project_root / "data"
    output_path = project_root / "data" / "analysis"
    output_path.mkdir(exist_ok=True)
    
    print("=== MovieLens Data Analysis ===")
    print(f"Project Root: {project_root}")
    print(f"Data Path: {data_path}")
    print(f"Output Path: {output_path}")
    
    # Load data
    print("\nLoading data...")
    ratings, movies = load_data(data_path)
    
    # Validate data structure
    validate_data_structure(ratings, movies)
    
    # Analyze sparsity
    sparsity_metrics = analyze_sparsity(ratings)
    
    # Create visualizations
    visualize_distributions(ratings, output_path)
    
    # Save summary
    summary_path = output_path / "data_analysis_summary.txt"
    with open(summary_path, 'w') as f:
        f.write("=== MovieLens Data Analysis Summary ===\n\n")
        f.write(f"Number of Users: {sparsity_metrics['n_users']}\n")
        f.write(f"Number of Movies: {sparsity_metrics['n_items']}\n")
        f.write(f"Number of Ratings: {sparsity_metrics['n_ratings']}\n")
        f.write(f"Sparsity: {sparsity_metrics['sparsity']:.4f} ({sparsity_metrics['sparsity'] * 100:.2f}%)\n\n")
        f.write(f"User Activity Mean: {sparsity_metrics['user_activity_mean']:.2f}\n")
        f.write(f"User Activity Median: {sparsity_metrics['user_activity_median']:.2f}\n")
        f.write(f"Item Popularity Mean: {sparsity_metrics['item_popularity_mean']:.2f}\n")
        f.write(f"Item Popularity Median: {sparsity_metrics['item_popularity_median']:.2f}\n\n")
        f.write(f"Cold Users (<=5 ratings): {sparsity_metrics['cold_users']}\n")
        f.write(f"Cold Items (<=5 ratings): {sparsity_metrics['cold_items']}\n")
    
    print(f"\nAnalysis complete. Summary saved to: {summary_path}")

if __name__ == "__main__":
    main()