package main

import (
	"encoding/json"
	"fmt"
	"io/ioutil"
	"log"
	"net/http"

	"github.com/minio/minio-go/v7"
	"github.com/minio/minio-go/v7/pkg/credentials"
)

type S3Nodes struct {
	S3Nodes []S3Node `json:"S3"`
}

type S3Node struct {
	Name      string
	Address   string
	AccessKey string
	SecretKey string
	Tls       bool
	Sets      []Set `json:"Sets"`
}

type Set struct {
	Name   string
	Bucket string
	Prefix string
	Filter string
}

func FileServer() http.Handler {
	return http.FileServer(http.Dir("./public")) // New code
}

func Next() http.Handler {
	return http.HandlerFunc(func(w http.ResponseWriter, r *http.Request) {
		fmt.Printf("Next\n")
	})
}

func Previous() http.Handler {
	return http.HandlerFunc(func(w http.ResponseWriter, r *http.Request) {
		fmt.Printf("Previous\n")
	})
}

func serveHTTP(port int, errs chan<- error) {

	mux := http.NewServeMux()

	mux.Handle("/", FileServer()) // New code
	mux.Handle("/next", Next())
	mux.Handle("/Previous", Previous())

	fmt.Printf("Starting server at port %d\n", port)
	var servestr = fmt.Sprintf(":%d", port)
	errs <- http.ListenAndServe(servestr, mux)
}

func main() {
	endpoint := "198.211.145.1:30991"
	accessKeyID := "admin"
	secretAccessKey := "mlstoreadmin"
	useSSL := false

	// Initialize minio client object.
	minioClient, err := minio.New(endpoint, &minio.Options{
		Creds:  credentials.NewStaticV4(accessKeyID, secretAccessKey, ""),
		Secure: useSSL,
	})
	if err != nil {
		log.Fatalln(err)
	}

	log.Printf("%#v\n", minioClient) // minioClient is now setup

	var port int = 7863

	s3data := S3Nodes{}
	file, _ := ioutil.ReadFile("config.json")
	err = json.Unmarshal([]byte(file), &s3data)
	if err != nil {
		fmt.Println(err)
	}
	fmt.Println(s3data)

	errs := make(chan error, 1) // a channel for errors
	go serveHTTP(port, errs)    // start the http server in a thread
	log.Fatal(<-errs)           // block until one of the servers writes an error
}
