#include <iostream>
#include <vector>

using namespace std;

const int N = 512;
vector<vector<int>> add(vector<vector<int>> A,
                        vector<vector<int>> B) {
    int n = A.size();
    vector<vector<int>> C(n, vector<int>(n, 0));

    for (int i = 0; i < n; i++) {
        for (int j = 0; j < n; j++) {
            C[i][j] = A[i][j] + B[i][j];
        }
    }

    return C;
}

vector<vector<int>> subtract(vector<vector<int>> A,
                             vector<vector<int>> B) {
    int n = A.size();
    vector<vector<int>> C(n, vector<int>(n, 0));

    for (int i = 0; i < n; i++) {
        for (int j = 0; j < n; j++) {
            C[i][j] = A[i][j] - B[i][j];
        }
    }

    return C;
}

void mulStressen(const vector<vector<int>>& A,const vector<vector<int>>& B,vector<vector<int>>& C){
    int n = A.size();

    if(n ==1){
        C[0][0] = A[0][0]*B[0][0];
        return;
    }

    int k = n/2;
    vector<vector<int>> A11(k, vector<int>(k));
    vector<vector<int>> A12(k, vector<int>(k));
    vector<vector<int>> A21(k, vector<int>(k));
    vector<vector<int>> A22(k, vector<int>(k));

    vector<vector<int>> B11(k, vector<int>(k));
    vector<vector<int>> B12(k, vector<int>(k));
    vector<vector<int>> B21(k, vector<int>(k));
    vector<vector<int>> B22(k, vector<int>(k));

    for (int i = 0; i < k; i++) {
        for (int j = 0; j < k; j++) {
            A11[i][j] = A[i][j];
            A12[i][j] = A[i][j + k];
            A21[i][j] = A[i + k][j];
            A22[i][j] = A[i + k][j + k];

            B11[i][j] = B[i][j];
            B12[i][j] = B[i][j + k];
            B21[i][j] = B[i + k][j];
            B22[i][j] = B[i + k][j + k];
        }
    }

    vector<vector<int>> M1(k, vector<int>(k));
    vector<vector<int>> M2(k, vector<int>(k));
    vector<vector<int>> M3(k, vector<int>(k));
    vector<vector<int>> M4(k, vector<int>(k));
    vector<vector<int>> M5(k, vector<int>(k));
    vector<vector<int>> M6(k, vector<int>(k));
    vector<vector<int>> M7(k, vector<int>(k));

    vector<vector<int>> T1, T2;

    // M1 = (A11 + A22) * (B11 + B22)
    T1 = add(A11, A22);
    T2 = add(B11, B22);
    mulStressen(T1, T2, M1);

    // M2 = (A21 + A22) * B11
    T1 = add(A21, A22);
    mulStressen(T1, B11, M2);

    // M3 = A11 * (B12 - B22)
    T1 = subtract(B12, B22);
    mulStressen(A11, T1, M3);

    // M4 = A22 * (B21 - B11)
    T1 = subtract(B21, B11);
    mulStressen(A22, T1, M4);

    // M5 = (A11 + A12) * B22
    T1 = add(A11, A12);
    mulStressen(T1, B22, M5);

    // M6 = (A21 - A11) * (B11 + B12)
    T1 = subtract(A21, A11);
    T2 = add(B11, B12);
    mulStressen(T1, T2, M6);

    // M7 = (A12 - A22) * (B21 + B22)
    T1 = subtract(A12, A22);
    T2 = add(B21, B22);
    mulStressen(T1, T2, M7);

    vector<vector<int>> C11 = add(
        subtract(add(M1, M4), M5), M7
    );

    vector<vector<int>> C12 = add(M3, M5);
    vector<vector<int>> C21 = add(M2, M4);

    vector<vector<int>> C22 = add(
        add(subtract(M1, M2), M3), M6
    );

    for (int i = 0; i < k; i++) {
        for (int j = 0; j < k; j++) {
            C[i][j] = C11[i][j];
            C[i][j + k] = C12[i][j];
            C[i + k][j] = C21[i][j];
            C[i + k][j + k] = C22[i][j];
        }
    }
}

int main(){
    vector<vector<int>> A(N, vector<int>(N,1));
    vector<vector<int>> B(N, vector<int>(N,2));
    vector<vector<int>> C(N, vector<int>(N,0));
    mulStressen(A,B,C);
    for(int i=0; i<C.size(); i++){
        for(int j=0; j<C[0].size(); j++){
            cout << C[i][j] << "  ";
        }
        cout << "\n";
    }
    return 0;
}