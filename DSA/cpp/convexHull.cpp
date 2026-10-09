
#include <iostream>
#include <vector>
using namespace std;

struct Point {
    int x, y;
};

Point pivot;

long long crossProduct(Point a, Point b, Point c) {
    return 1LL * (b.x - a.x) * (c.y - a.y)
         - 1LL * (b.y - a.y) * (c.x - a.x);
}

long long distanceSquared(Point a, Point b) {
    long long dx = a.x - b.x;
    long long dy = a.y - b.y;
    return dx * dx + dy * dy;
}

bool comparison(const Point& a, const Point& b) {
    long long cross = crossProduct(pivot, a, b);

    if (cross != 0)
        return cross > 0;

    return distanceSquared(pivot, a)
         < distanceSquared(pivot, b);
}

vector<Point> convexHull(vector<Point>& points) {
    int n = points.size();

    if (n <= 1)
        return points;

    int lowest = 0;

    for (int i = 1; i < n; i++) {
        if (points[i].y < points[lowest].y ||
           (points[i].y == points[lowest].y &&
            points[i].x < points[lowest].x)) {
            lowest = i;
        }
    }

    Point temp = points[0];
    points[0] = points[lowest];
    points[lowest] = temp;

    pivot = points[0];

    for (int i = 2; i < n; i++) {
        Point key = points[i];
        int j = i - 1;

        while (j >= 1 && comparison(key, points[j])) {
            points[j + 1] = points[j];
            j--;
        }

        points[j + 1] = key;
    }

    vector<Point> sorted;
    sorted.push_back(points[0]);

    for (int i = 1; i < n; i++) {
        while (i + 1 < n &&
               crossProduct(pivot, points[i], points[i + 1]) == 0) {
            i++;
        }

        sorted.push_back(points[i]);
    }

    if (sorted.size() < 3)
        return sorted;

    vector<Point> hull;

    hull.push_back(sorted[0]);
    hull.push_back(sorted[1]);

    for (int i = 2; i < (int)sorted.size(); i++) {
        while (hull.size() >= 2 &&
               crossProduct(hull[hull.size() - 2],
                            hull.back(), sorted[i]) <= 0) {
            hull.pop_back();
        }

        hull.push_back(sorted[i]);
    }

    return hull;
}

int main() {
    vector<Point> points = {
        {5, 5}, {1, 1}, {9, 4}, {2, 8}, {4, 4},
        {7, 4}, {0, 5}, {5, 9}, {3, 3}, {8, 7},
        {6, 2}, {2, 5}, {8, 1}, {4, 7}, {1, 3},
        {5, 3}, {2, 2}, {4, 1}, {6, 6}, {3, 5}
    };

    vector<Point> hull = convexHull(points);

    for (const auto& p : hull) {
        cout << "(" << p.x << "," << p.y << ") ";
    }

    cout << endl;

    return 0;
}
