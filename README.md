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

debouncing itu semacam ngasih jeda sebelum menjalankan proses, jadi setiap user mengetik timer sebelumnya dibatalin terus mulai lagi dari awal, di project ini aku pakai jeda 450 ms jadi request pencarian baru dikirim setelah user berhenti mengetik selama waktu tersebut. kenapa penting, karena kalo setiap huruf langsung ngirim request bakal banyak request yang sebenernya ga perlu, misalnya pas mau ngetik research malah ngirim pencarian dari r, re, res dan seterusnya, jadinya lebih berat buat server dan tampilan juga bisa berubah ubah terus, dengan debouncing pencarian jadi lebih efisien dan enak dipakai

2. Jelaskan fungsi dari penggunaan await ketika kita menggunakan fetch()! Apa yang akan terjadi jika kita tidak menggunakan await?

fetch itu proses asynchronous yang hasil awalnya berupa Promise, await dipakai untuk menunggu Promise tersebut selesai sebelum lanjut ke baris berikutnya dalam fungsi async, jadi response yang kita terima sudah berupa object Response yang bisa dicek statusnya, setelah itu response.json() juga perlu ditunggu karena proses membaca dan mengubah isi respons jadi object javascript juga asynchronous. selama nunggu bukan berarti seluruh browser berhenti, yang ditunda cuma kelanjutan fungsi tersebut

kalo ga pakai await dan hasil fetch langsung dipakai seolah olah sudah berupa Response, yang kita pegang masih Promise jadi response.json() bakal eror karena method tersebut bukan milik Promise. sebenernya tetap bisa tanpa await dengan memakai .then() dan .catch(), yang penting hasil requestnya tetap ditangani setelah prosesnya selesai

3. Jelaskan apa itu serangan XSS (Cross-Site Scripting) dan mengapa data yang ditampilkan melalui AJAX/JavaScript lebih rentan terhadap serangan ini daripada data yang ditampilkan langsung melalui template Django!

XSS itu serangan ketika input dari user berisi kode berbahaya lalu masuk ke halaman dan dijalankan browser sebagai kode, misalnya input judul berisi tag dengan onerror yang akhirnya bisa menjalankan javascript untuk mengambil data yang dapat diakses halaman atau melakukan aksi memakai sesi user

data lewat AJAX sebenernya ga otomatis berbahaya karena JSON sendiri cuma data, masalahnya muncul pas javascript menyisipkan nilai tersebut ke HTML misalnya lewat innerHTML tanpa escaping, browser bisa menganggap input tadi sebagai markup dan menjalankan kode di dalamnya. sementara template Django secara default punya autoescaping untuk nilai teks sehingga karakter seperti < dan > ditampilkan sebagai teks, jadi perlindungan ini harus kita tangani sendiri saat menyusun tampilan lewat javascript

di project ini aku pakai textContent untuk menampilkan nilai teks supaya input ga dianggap sebagai HTML, terus input judul, deskripsi dan caption dibersihkan di method clean pada ModelForm menggunakan strip_tags, tapi pembersihan server ini tetap perlu dibarengi cara menampilkan data yang aman di browser, terutama kalo ada data lama yang belum dibersihkan


AI
menggunakan ai untuk membantu memeriksa kesesuaian project dengan checklist tugas, membantu evaluasi halaman experience dan about agar pengambilan data, pencarian sesuai framework AJAX, membantu penerapan debouncing, serta pengecekan permission dan perlindungan XSS, juga membantu proses testing