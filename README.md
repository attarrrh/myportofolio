#TUGAS 1

1. Pada Tutorial dan Tugas 1, Anda diberi kebebasan untuk menentukan tampilan dari website portofolio Anda. Saat Anda merancang struktur HTML yang digunakan, apakah Anda menggunakan elemen semantik HTML5 seperti <section>, <article>, atau <aside>? Jika iya, bagaimana elemen tersebut membantu Anda dalam membuat static web? Jika tidak, mengapa tanpa elemen tersebut sudah memenuhi kebutuhan desain Anda?

ya saya menggunakan elemen elemen tersebut untuk membantu mempermudah penyusunan struktur agar lebih rapih dan readdable, kalo gapake takutnya jadi redundant dan penuh sama div div doang

2. Ketika Anda mengatur CSS Anda agar tetap responsive, tantangan tata letak apa yang Anda temukan? Bagaimana Anda mengevaluasi elemen mana yang harus diubah posisinya atau diprioritaskan ukurannya saat berpindah dari tampilan desktop ke mobile?

tantangan utama saat mengatur CSS agar responsive adalah mastiin susunan gridnya ga numpuk di HP. aku coba evaluasi by trial error pokoknya sampe enak kalo dibuka di hp, jadi elemen yang awalnya berjajar ke samping kayak daftar skill aku ubah urutannya jadi ke bawah jadi satu kolom dll

3. Website yang Anda buat saat ini adalah static web murni. Batasan apa yang Anda rasakan saat mencoba menyajikan informasi pada portofolio Anda secara optimal? Berdasarkan batasan tersebut, fungsionalitas dinamis apa yang paling ingin Anda persiapkan dan tambahkan pada iterasi proyek selanjutnya?

batasan yang aku rasakan ada pada bagian edit manual hampir semuanya mulai dari kontainer, masukin nama, masukin experience, masukin gambar dll, kayaknya kalo kita langsung sambungin sql data base gitu bakal lebih enak

Attar Rais Hakam
2506656495

AI
menggunakan skill web artefact yang ada di claude dengan pendekatan referensif mencari inspirasi sebagai bahan referensi kemudian minta saran dan adjusment terhadap web template awal yang diberikan, kemudian eksplorasi berdasarkan konsep yang ada internet dan referensi lain, menambahkan fitur, menambahkan animasi, menambahkan hal hasil eksplorasi, editing dan cleaning, refactor beberapa kesalahan ataupun hal yang dirsa kurang, finishing dan meminta feedback evaluasi dan masukan terkait apa yang bisa di tambahkan kedepannya

#TUGAS2
1. Jelaskan alur yang terjadi ketika pengguna membuka halaman portofolio baru, mulai dari permintaan yang diterima proyek hingga data ditampilkan pada browser. Dalam jawabanmu, jelaskan peran urls.py proyek, urls.py aplikasi, view, model, dan template.

jadi browser ngirim reqnya dulu ke alamat tujuan misalnya /experience, terus lanjut django membaca dulu urls proyek yang mana dari urls itu di terusin ke path urls yang ada di main, di main lanjut lagi ke urls dia ini mengecek kecocokan path experience dengan yang ada di daftar biasanya terdapat inisiasi path seperti "path("experience/", show_experience, name="show_experience"),", django disini tau kalo path itu di tangani oleh fungsi dengan nama show_exp, fungsi ini adanya di views setelah dia dijalankan di dalamnya views manggil dan ngambil semua data dari model terkait "experience.object.all", selanjutnya data model dimasukan kedalam context, kemudian views ini manggil requwst experience.html untuk ditampilkan, next django ngebuka experience.html dan ngirim respons tersebut ke browser

2. Mengapa data untuk bagian portofolio baru sebaiknya disimpan pada model dan tidak ditulis langsung di dalam template? Jelaskan dampaknya terhadap kemudahan pemeliharaan dan pengembangan aplikasi.

kalau data ditulis langsung di template tidak hanya membuang tenaga untuk menulisnya di html secara manual, tetapi juga merepotkan jika setiap kali ada data baru harus mengedit file htmlnya lagi dan mencari bagiannya satu persatu, dan bagaimanajika data yang ingin di input merupakan bigdata prosesnya jadi lambat dan rawan human error sangat tidak efektif bagi pengembangan website waktu selanjutnya

3. Apa perbedaan fungsi makemigrations dan migrate pada Django? Berikan contoh perubahan model yang mengharuskanmu menjalankan kedua perintah tersebut.
makemigrations membaca perubahan yang kamu buat pada file models, lalu membuat file migrasi baru di folder main/migrations biasanya berisi instruksi perubahan, intinya disini database belum diubah sama sekali, baru dibuat semacam skemaa aja

migrate menjalankan instruksi dari file migrasi tersebut ke database, disini struktur tabel di database baru mulai di ubah, misalnya membuat tabel baru atau menambah kolom


AI
menggunakan ai untuk membantu mengulang proses pembuatan app yang sebelumnya sudah dilakukan pada tutorial 2 untuk membuat experience kali ini bagaimana jika membuat app aboutme berisi galeri gamber pengalaman atau hobi yang sering aku lakukan, sekaligus membantu melakukan strukturisasi css serta membantu jika terjadi eror terutama pada tahap explorasi dan commiting git


#TUGAS 3
1. Jelaskan mengapa kita menggunakan ModelForm pada Django alih-alih membuat form HTML secara manual. Selain itu, jelaskan pula mengapa kita diwajibkan menambahkan {% csrf_token %} pada form tersebut!

karena mengikuti prinsip DRY yang sebelumya kita terapkan pada base html, kurang lebih konsepnya sama dimana kita bisa mempersingkat dan meningkatkan efisiensi inputing agar tidak melakukan penulisan input manual berulang dengan langsung menurunkannya dari model dan form, mengapa wajib mengunakan csrf token, karena csrf token semacam sistem keamanan yang mencegah project Django dari serangan csrf dengan menolak segala post tanpa adanya token tersebut, token ini berfungsi sebagai sistem authentifikasi yang memberikan token unik persesi agar user dapat melakukan post request

2. Pada Tutorial 03, kita membahas format data JSON dan XML. Mengapa JSON lebih disukai dalam pengembangan aplikasi web modern dibandingkan XML?

karena penulisannya lebih ringkas lebih mudah untuk ditulis dan modifikasi, struktur yang dimiiliki JSON lebih sederhana dan native dengan javascript membuatnya fleksibel tanpa perlu library tambahan untuk melakukan parsing

3. Jelaskan alur yang terjadi saat kamu menggunakan fungsi view untuk mengembalikan data portofoliomu dalam bentuk JSON. Mengapa kita perlu melakukan proses serialization pada model Django sebelum datanya dikembalikan?

Alur dimulai dari menerima request dari user, masuk ke urls.py arahkan ke view sesuai dengan request, masuk kedalam view ambil data dari database, masuk ke bagian serializer yang akan mengubah object dari database jadi string JSON, terakhir dikirim kembali ke user melalui HttpResponse

mengapa perlu di lakukan serialization, karena http cuma dapat mengirimkan object berupa byte/text, sementara data sebelumnya berbentuk python object dan atau object method, sehingga perlu dilakukan serialization sebagai proses penerjemahan object python tersebut menjadi text/byte yang bersifat lebih universal dan dapat dipahami oleh sistem apapun

AI
menggunakan ai untuk membantu memahami alur rancangan penugasan serta keterkaitan materi yang digunakan pada tutorial dengan apa yang digunakan untuk tugas ini, membantu proses pengecekan kode akhir dan refactoring jika diperlukan, membantu memahami lebih lanjut terkait perbedaan format data bagaimana penerapanya dalam tutor serta tugas dan juga membantu meelakukan perbaikan ketika terdapat eror terutama berurusan dengan git.


#TUGAS 5
1. Jelaskan apa itu debouncing dan mengapa teknik ini penting diterapkan pada fitur pencarian yang menggunakan AJAX!

debouncing itu semacam ngasih jeda sebelum menjalankan proses, jadi setiap user mengetik timer sebelumnya dibatalin terus mulai lagi dari awal, di project ini aku pakai jeda 450 ms jadi request pencarian baru dikirim setelah user berhenti mengetik selama waktu tersebut. ini biar kalo setiap huruf langsung ngirim request bakal banyak request yang sebenernya ga perlu, misalnya pas mau ngetik research malah ngirim pencarian dari r, re, res dan seterusnya, jadinya lebih berat buat server dan tampilan juga bisa berubah ubah terus, dengan debouncing pencarian jadi lebih efisien dan enak dipakai

2. Jelaskan fungsi dari penggunaan await ketika kita menggunakan fetch()! Apa yang akan terjadi jika kita tidak menggunakan await?

fetch itu proses asynchronous yang hasil awalnya berupa Promise, await dipakai untuk menunggu Promise tersebut selesai sebelum lanjut ke baris berikutnya dalam fungsi async, jadi response yang kita terima sudah berupa object Response yang bisa dicek statusnya, setelah itu response.json() juga perlu ditunggu karena proses membaca dan mengubah isi respons jadi object javascript juga asynchronous

kalo ga pakai await dan hasil fetch langsung dipakai seolah olah sudah berupa Response, yang kita pegang masih Promise jadi response.json() bakal eror karena method tersebut bukan milik Promise. sebenernya tetap bisa tanpa await dengan memakai .then() dan .catch(), yang penting hasil requestnya tetap ditangani setelah prosesnya selesai

3. Jelaskan apa itu serangan XSS (Cross-Site Scripting) dan mengapa data yang ditampilkan melalui AJAX/JavaScript lebih rentan terhadap serangan ini daripada data yang ditampilkan langsung melalui template Django!

XSS itu serangan ketika input dari user berisi kode berbahaya lalu masuk ke halaman dan dijalankan browser sebagai kode, misalnya input judul berisi tag dengan onerror yang akhirnya bisa menjalankan javascript untuk mengambil data yang dapat diakses halaman atau melakukan aksi memakai sesi user

data lewat AJAX sebenernya ga otomatis berbahaya karena JSON sendiri cuma data, masalahnya muncul pas javascript menyisipkan nilai tersebut ke HTML misalnya lewat innerHTML tanpa escaping, browser bisa menganggap input tadi sebagai markup dan menjalankan kode di dalamnya. sementara template Django secara default punya autoescaping untuk nilai teks sehingga karakter seperti < dan > ditampilkan sebagai teks, jadi perlindungan ini harus kita tangani sendiri saat menyusun tampilan lewat javascript

disinii pakai textContent untuk menampilkan nilai teks supaya input ga dianggap sebagai HTML, terus input judul, deskripsi dan caption dibersihkan di method clean pada ModelForm menggunakan strip_tags, tapi pembersihan server ini tetap perlu dibarengi cara menampilkan data yang aman di browser, terutama kalo ada data lama yang belum dibersihkan


AI
menggunakan ai untuk membantu memeriksa kesesuaian project dengan checklist tugas, membantu evaluasi halaman experience dan about agar pengambilan data, pencarian sesuai framework AJAX, membantu penerapan debouncing, serta pengecekan permission dan perlindungan XSS, juga membantu proses testing


#TUGAS 6

1. Jelaskan apa yang dimaksud dengan REST dan mengapa mengembalikan JSON saja belum cukup untuk menyebut sebuah API sebagai RESTful! Jelaskan pula perbedaan PUT dan PATCH beserta contoh kapan masing-masing sebaiknya digunakan!

REST itu gaya arsitektur untuk menyusun komunikasi antara client dan server, dimana data dianggap sebagai resource dan tindakan terhadap data tersebut dibedakan lewat method HTTP. misalnya di project ini `/api/v1/gallery/` menunjuk kumpulan item galeri, GET dipakai buat membaca sedangkan POST buat menambah, kemudian `/api/v1/gallery/<uuid>/` menunjuk satu item yang bisa diubah atau dihapus

kalo cuma ngembaliin JSON belum tentu RESTful karena JSON itu format datanya aja, sementara REST juga berhubungan dengan cara menyusun resource, penggunaan method, status HTTP dan prinsip stateless, jadi bukan sekadar asal response bentuknya JSON. pada tutorial ini kita masih memakai session login Django sehingga bukan implementasi REST yang sepenuhnya stateless, tapi pengaturan resource dan kontrak API-nya tetap mengikuti pola REST yang dipelajari

PUT dipakai ketika ingin mengganti representasi data secara lengkap, jadi field wajib perlu dikirim lagi, misalnya mengganti judul, tipe media dan seluruh informasi yang diperlukan pada item galeri. PATCH dipakai ketika cuma mau mengubah sebagian, misalnya hanya mengganti caption tanpa mengirim ulang judul atau foto, makanya form edit di project ini memakai PATCH supaya file lama tetap dipertahankan kalo ga ada upload baru

2. Jelaskan peran serializer pada Django REST Framework! Apa keuntungannya dibandingkan merakit dictionary secara manual dengan JsonResponse seperti pada Tutorial 05?

serializer itu penerjemah sekaligus pemeriksa data, saat GET dia mengubah object model jadi tipe data python yang bisa dirender ke JSON, sedangkan saat POST atau PATCH dia membaca input, melakukan validasi lalu menyimpan jika datanya valid. hasil serializer belum langsung berupa string JSON, proses menjadikannya isi response dilakukan renderer DRF

sebelumnya kita perlu menyusun dictionary satu persatu dan memisahkan validasi lewat ModelForm, sekarang dengan ModelSerializer field bisa diturunkan dari model dan dipilih secara eksplisit, aturan input bisa ditulis di validate_title atau validate_caption, terus jumlah star dan status star bisa ditambahkan sebagai field hasil perhitungan yang read-only. jadinya lebih rapih dan ga perlu mengulang susunan data maupun validasi di setiap view, tapi validasi form lama ga otomatis dijalankan serializer jadi aturan yang diperlukan tetap harus ditulis pada jalur API

3. Jelaskan perbedaan autentikasi dan otorisasi pada Django REST Framework! Mengapa hak akses harus diperiksa dengan permission class di server, bukan hanya dengan menyembunyikan tombol di template?

autentikasi itu mengenali siapa yang mengirim request, di project ini SessionAuthentication memakai session login Django untuk mengisi request.user. otorisasi itu tahap sesudahnya yaitu memeriksa user tersebut boleh melakukan apa, misalnya pengguna biasa boleh star tapi ga boleh edit, Editor boleh PUT/PATCH tapi ga boleh create/delete, sementara superuser boleh mengelola semuanya

menyembunyikan tombol cuma membantu tampilan, bukan membatasi request yang masuk. walaupun tombol hapus ga muncul, user masih bisa mengirim DELETE sendiri lewat console atau aplikasi lain, jadi permission class di server tetap harus menolak sebelum perubahan dijalankan. view lama juga perlu mengikuti aturan yang sama supaya pembatasan di API ga bisa dilewati lewat alamat form lama

4. Jelaskan mengapa permintaan yang mengubah data tetap memerlukan token CSRF ketika API memakai SessionAuthentication! Mengapa test yang memakai force_authenticate tidak cukup untuk membuktikan bahwa perlindungan CSRF berjalan?

karena browser otomatis menyertakan cookie session saat mengirim request yang sesuai, ada risiko user yang sedang login diarahkan untuk mengirim request dari situs lain tanpa sadar. walaupun body request berbentuk JSON atau endpointnya memakai DRF, session tetap dipakai untuk mengenali user, jadi permintaan yang mengubah data tetap perlu token CSRF yang diperiksa server, disini dikirim melalui header X-CSRFToken termasuk saat memberi star

force_authenticate itu jalan pintas untuk menentukan user saat test, dia ga menjalankan alur autentikasi session sungguhan sehingga ga cukup buat membuktikan CSRF berfungsi. karena itu dipakai APIClient(enforce_csrf_checks=True) dan .login(), lalu dicoba request tanpa token yang harus ditolak 403 dan database tetap sama, setelah token diambil dari halaman, request yang punya izin dan token valid bisa berhasil. dengan begitu yang diuji bukan cuma permission, tapi juga perlindungan CSRF pada session yang sebenarnya


AI
menggunakan ai untuk membantu mengecek checklist Tugas 6 terhadap kode Tutorial 7 dan bagaimana penerapan apa yang sebelumnya dikerjakan pada tutorial 7 kedalam tugas 6 ini. kemudian ai juga digunakan untuk merancang alur perubahan serta membantu evaluasi code akhir, juga membantu memenuhi testing yang masih kurang.
