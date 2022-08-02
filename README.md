# auto_dhlottery
동행복권 자동 구매 

## How to config
`~/.dh/config.json` 내에 id, pw 및 각 복권의 config를 정의한다.

```
{
    "pw": "{password}" ,
    "id": "{id}",
    "lotto645_numbers": [
        [1,2,3,4,5,6], 
        [1,2,3], 
        [1,2,3]
    ],
    "lotto645_number_per_purchase": 5
}
```

## Lotto6/45

```
python ./purchase_lotto645.py
```