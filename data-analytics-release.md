### Deployment

#### Bangor

---

1.  Switch to `arcca` branch.

    `git checkout arcca`

2.  Source environment.

    `source /path/to/venv`

3.  Run database migrations.

    `python3 manage.py migrate`

4.  Load data fixtures.

    ```
    python3 manage.py loaddata \
       access_methods.json \
       applications.json \
       os.json \
       hardware_groups.json \
       partitions.json
    ```

5.  Migrate PI text field.

    ```
    python3 manage.py migrate_pi_text_field
    ```

6.  Load in historical data.

    -   Import daily compute.

        ```
        python3 manage.py import_historical_daily_compute \
           --input_dir=path_to_bz2_files_to_import \
           --output_dir=path_to_move_bz2_files_to_once_processed
        ```

    -   Import daily compute LIGO.

        ```
        python3 manage.py import_historical_daily_compute_ligo \
           --input_dir=path_to_bz2_files_to_import \
           --output_dir=path_to_move_bz2_files_to_once_processed
        ```

    -   Import user last login.

        ```
        python3 manage.py import_historical_user_last_login \
           --input_dir=path_to_csv_files_to_import \
           --output_dir=path_to_move_csv_files_to_once_processed
        ```

    -   Import weekly storage.

        ```
        python3 manage.py import_historical_weekly_storage \
           --input_dir=path_to_csv_files_to_import \
           --output_dir=path_to_move_csv_files_to_once_processed
        ```

#### Cardiff

---


### Data Import

#### Find date range of LIGO file.

```
python3 manage.py find_date_range_of_ligo_file \
   --file=path_to_ligo_log_file.out
```

#### Import LIGO daily compute stats.

```
python3 manage.py import_daily_compute_ligo \
   --file=path_to_stats_file.out
   -d 31 \
   -m 10 \
   -y 2020 \
   -s CF
```

#### Import daily compute stats.

```
python3 manage.py import_daily_compute \
   --file=path_to_stats_file.out
   -d 31 \
   -m 10 \
   -y 2020 \
   -s CF
```

#### Import user last login stats.

```
python3 manage.py import_user_last_login \
   --file=path_to_user_last_login.csv
```

#### Import weekly storage stats.

```
python3 manage.py import_weekly_storage \
   --homefile=path_to_home_file.csv \
   --scratchfile=path_to_scratch_file.csv \
   -d 21 \
   -m 11 \
   -y 2020 \
   -s CF
```
