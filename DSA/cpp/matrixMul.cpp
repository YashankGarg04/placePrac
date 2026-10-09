#include <iostream>
#include <vector>

using namespace std;

const int n = 512;

void matrixMul(vector<vector<int>> A,vector<vector<int>> B,vector<vector<int>>& C ){
    int i, j, k;
    for(i = 0; i<A.size();i++){
        for(j = 0; j<B[0].size(); j++){
            for(k=0; k<A[0].size();k++){
                C[i][j] += A[i][k] * B[k][j];
            }
        }
    }
}

int main(){
    vector<vector<int>> A(n, vector<int>(n,1));
    vector<vector<int>> B(n, vector<int>(n,2));
    vector<vector<int>> C(n, vector<int>(n));
    matrixMul(A,B,C);
    for(int i=0; i<C.size(); i++){
        for(int j=0; j<C[0].size(); j++){
            cout << C[i][j] << "  ";
        }
        cout << "\n";
    }
    return 0;
}