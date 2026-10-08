#include <iostream>
#include <vector>
using namespace std;

void merge(vector<int>& arr, int left, int mid, int right){
    int n1 = mid - left +1;
    int n2 = right - mid;
    vector<int> L(n1), R(n2);

    for(int i=0; i<n1;i++){
        L[i] = arr[left + i];
    }
    for(int j=0;j<n2;j++){
        R[j] = arr[mid +1 + j];
    }

    int i=0,j=0;
    int k= left;

    while (i<n1 && j<n2){
        if(L[i] <= R[j]){
            arr[k] = L[i];
            i++;
        }
        else{
            arr[k] = R[j];
            j++;
        }
        k++;
    }

    while(i<n1){
        arr[k] = L[i];
        i++;
        k++;
    }
    while(j<n2){
        arr[k] = R[j];
        j++;
        k++;
    }
}

void mergesort(vector<int>& arr,int left, int right){
    if (left >= right){
        return;
    }

    int mid = left + (right - left)/2;
    mergesort(arr, left, mid);
    mergesort(arr,mid+1, right);
    merge(arr, left, mid, right);
}

vector<int,int> twoSum(vector<int>& arr, int sum){
    int size = arr.size();
    int left = 0;
    int right = size-1;
    int flag =0;
    while(left<= right){
        int a = arr[left]+arr[right];
        if(a == sum){
            flag =1;
            return {left,right};
        }
        else if(a<sum){
            left++;
        }
        else{
            right--;
        }
    }
    if(flag==0){
        cout << "No Sum Found";
        return {0,0};
    }
}


int main (){
    vector<int> arr= {73,23,4,22,92,14,2,1,33};
    int size = arr.size();
    int left = 0;
    int right = size-1;
    int sum = 55;
    int i,j;
    mergesort(arr, left, right);
    vector<int,int> i,j = twoSum(arr, sum);

    return 0;
}