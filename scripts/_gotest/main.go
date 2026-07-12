package main

import (
	"fmt"
	"io"
	"os"
	"strings"
)

func count_partitions(s string) int64 {
m := len(s)
isPal := make([][]bool, m)
for i := range isPal { isPal[i] = make([]bool, m) }
for i := 0; i < m; i++ { isPal[i][i] = true }
for length := 2; length <= m; length++ {
  for i := 0; i+length-1 < m; i++ {
    j := i+length-1
    if s[i] == s[j] && (length == 2 || isPal[i+1][j-1]) { isPal[i][j] = true }
  }
}
dp := make([]int64, m+1)
dp[0] = 1
for i := 1; i <= m; i++ {
  var total int64 = 0
  for j := 0; j < i; j++ {
    if isPal[j][i-1] { total += dp[j] }
  }
  dp[i] = total
}
result := dp[m]
return result
}

func main() {
data, _ := io.ReadAll(os.Stdin)
s := strings.TrimSpace(string(data))
result := count_partitions(s)
fmt.Println(result + 0)
}
