# 10-HaYangSongE-BE



## Django Management Command

`
python manage.py startapp [AppName]
`

`
python manage.py makemigrations
`

`python manage.py migrate
`

`python manage.py createsuperuser
`

`python manage.py collectstatic
`

`python manage.py runserver
`

## Git Command

### Control Staging area
`
git add [regx]
`

`
git commit -m [commit msg]
`

### Control Remote repository
`
git push [remote] [branch]
`

`git pull [remote] [branch]`  

### Control Branch

`
git branch [Name]
`

`
git merge [Name]
`

## Local Test

```bash
git clone https://github.com/KnS-hacks/10-HaYangSongE-BE

가상환경 ~

pip install --upgrade pip

pip install -r requirements.dev.txt

python manage.py makemigrations

python manage.py migrate
```

## API 명세서
[NOTION](https://www.notion.so/API-2b18be0c61c3464e996b991676b87c82)

[Postman](https://www.postman.com/bold-satellite-818814/workspace/vacstage/overview)