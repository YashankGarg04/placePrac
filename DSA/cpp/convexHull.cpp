#include <iostream>
#include <vector>
using namespace std;
struct Point {
        int x,y;
    };
bool comparison(const Point& a, const Point& b){
    if (a.x != b.x){
        return a.x < b.x;
    }
    return a.y<b.y;
}
int partition(vector<Point>& points, int low, int high){
    Point pivot = points[high];
    int i = low - 1;

    for(int j=low; j<high; j++){
        if(comparison(points[j], pivot)){
                i++;
                Point temp = points[i];
                points[i] = points[j];
                points[j] = temp;
        }
    }
    Point temp = points[i+1];
    points[i+1]= points[high];
    points[high] = temp;

    return i+1;
}

void quickSort2D(vector<Point>& points, int low, int high){
    if (low<high){
        int pivot_index = partition(points, low, high);
        quickSort2D(points, low, pivot_index - 1);
        quickSort2D(points, pivot_index + 1, high);
    }

}

long long crossProduct(Point a, Point b, Point c){
    return 1LL * (b.x - a.x)*(c.y-b.y) - 1LL*(b.y - a.y)*(c.x - b.x);
}

vector<Point> convexHull(vector<Point>& points){
    int n = points.size();
    if(n<=3){
        return points;
    }
    vector<Point> hull;

    for(int i = 0; i<n;i++){
        while(hull.size() >=2 && crossProduct(hull[hull.size() - 2], hull.back(), points[i])<=0){
            hull.pop_back();
        }
        hull.push_back(points[i]);
    }

    int t = hull.size();
    for(int i=n-2;i>=0;i--){
        while(hull.size() > t && crossProduct(hull[hull.size()-2],hull.back(), points[i])<=0){
            hull.pop_back();
        }
        hull.push_back(points[i]);
    }
    hull.pop_back();
    
    return hull;
}

int main(){
    vector<Point> points = {
    {5, 5}, {1, 1}, {9, 4}, {2, 8}, {4, 4}, 
    {7, 4}, {0, 5}, {5, 9}, {3, 3}, {8, 7}, 
    {6, 2}, {2, 5}, {8, 1}, {4, 7}, {1, 3}, 
    {5, 3}, {2, 2}, {4, 1}, {6, 6}, {3, 5}
    };
    quickSort2D(points, 0, points.size() - 1);
    for(const auto& p : points){
        cout << "("<<p.x<<","<<p.y<<") ;";
    }
    cout << "\n";
    vector<Point> hull = convexHull(points);
    for(const auto& p : hull){
        cout << "("<<p.x<<","<<p.y<<") ;";
    }
    return 0;
}