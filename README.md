STUDENT PERSONAL RECORD MANAGER

FEATURES-
1---student account creation
2---validating student
3---storing student data
4---creation of notes
5---manipulating notes
6---uploading files
7---manipulating files
8---creating excel sheet

mysql connect,sessions,request handling
(get,post,put,delete),jinja dynamic

mysql tables--student_info,notes,files

notes table;
notes_idtitlenote_content,created_at added_by
mysql> create table notes(notes_id int primary key auto_increment,title varchar(20) unique key not null,
    -> note_content text,created_at timestamp default current_timestamp(),added_by varchar(100),
    -> foreign key(added_by) references stu_info(email) on update cascade on delete cascade);
