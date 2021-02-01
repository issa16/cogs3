### User Guide

#### User

**Overview**

---

A user that is not a technical lead of a project or a member of staff of MySCW has a restricted view of their compute and storage data analytics.

Upon successful login to MySCW, a user’s view will default to the homepage that will display the following four charts: 

1. Efficiency per month.
2. Number of jobs per month.
3. Rate of usage per month.
4. Cumulative total usage per month.

All of the above charts will default to display the user’s usage over the last twelve months.

**Insert images**



**Filter Chart Data**

---

By default, the charts will display the cumulative totals of a user's usage for the projects in which a user has a valid project membership. A user can filter the results on a per-project basis by selecting the ‘Project Filter' dropdown option and selecting a project.

**Insert images**



#### Technical Lead

**Overview**

---

In addition to the default users view as described in the ‘User' section above, a technical lead of a project will have the option to view the compute and storage data analytics for their projects.

Upon successful login to MySCW, a technical lead will have an additional link in the left sidebar named ‘Data Analytics’. 

**Insert images**

By default, the link will take the user to the data analytics page of their most recently created project on MySCW.

**Insert images**



**Filter Projects**

---

Technical leads that are linked to multiple SCW projects can switch between projects by selecting the ‘Project Filter' dropdown option and selecting a project.

**Insert images**



**Project Overview Data**

---

**Insert images**

<table>
    <thead>
        <tr>
            <th><strong>ID</strong></th>
            <th><strong>Title</strong></th>
            <th><strong>Description</strong></th>
        </tr>
    </thead>
    <tbody>
        <tr>
            <td>1</td>
            <td>Principle Investigator</td>
            <td>Project’s PI name and institution.</td>
        </tr>
        <tr>
            <td>2</td>
            <td>Technical Lead</td>
            <td>Project’s Technical Lead's name.</td>
        </tr>
        <tr>
            <td>3</td>
            <td>Start date</td>
            <td>Project’s start date.</td>
        </tr>
        <tr>
            <td>4</td>
            <td>End date</td>
            <td>Project’s end date.</td>
        </tr>
        <tr>
            <td>5</td>
            <td>Institution</td>
            <td>Project’s Technical Lead’s institution.</td>
        </tr>
        <tr>
            <td>6</td>
            <td>Efficiency</td>
            <td>Project’s overall efficiency.</td>
        </tr>
        <tr>
            <td>7</td>
            <td>Home storage allocation</td>
            <td>Project’s home storage allocation - N/A if empty.</td>
        </tr>
        <tr>
            <td>8</td>
            <td>Scratch storage allocation</td>
            <td>Project’s scratch storage allocation - N/A if empty.</td>
        </tr>
        <tr>
            <td>9</td>
            <td>Total allocated core hours</td>
            <td>Project’s total allocated core hours.</td>
        </tr>
        <tr>
            <td>10</td>
            <td>Total number of core hours</td>
            <td>Project’s total number of elapsed core hours consumed over all time.</td>
        </tr>
        <tr>
            <td>11</td>
            <td>Total number of CPU hours</td>
            <td>Project’s total number of CPU hours consumed over all time.</td>
        </tr>
        <tr>
            <td>12</td>
            <td>Total number of Slurm jobs</td>
            <td>Project’s total number of jobs run through Slurm over all time.</td>
        </tr>
        <tr>
            <td>13</td>
            <td>Principal Investigator’s Projects chart</td>
            <td>Displays the number of active, dormant, inactive and retired projects for the project’s PI.</td>
        </tr>
        <tr>
            <td>14</td>
            <td>Users status chart</td>
            <td>Displays the number of active, dormant and inactive users for the project.</td>
        </tr>
    </tbody>
</table>



**Project Compute Data**

---

**Insert images**

<table>
    <thead>
        <tr>
            <th><strong>ID</strong></th>
            <th><strong>Title</strong></th>
            <th><strong>Description</strong></th>
        </tr>
    </thead>
    <tbody>
        <tr>
            <td>1</td>
            <td>Start date</td>
            <td>Start date of the compute consumption query.</td>
        </tr>
        <tr>
            <td>2</td>
            <td>End date</td>
            <td>End date of the compute consumption query.</td>
        </tr>
        <tr>
            <td>3</td>
            <td>Core Partitions data in date range</td>
            <td>CPU Time, Wait Time, Wall Time and Efficiency of the project on the <strong>core partitions</strong> within the query’s start and end date.</td>
        </tr>
        <tr>
            <td>4</td>
            <td>Core Partitions data to present</td>
            <td>CPU Time, Wait Time, Wall Time and Efficiency of the project on the <strong>core partitions</strong> from the project start date to the present date.</td>
        </tr>
        <tr>
            <td>5</td>
            <td>Researcher Funded Partitions data in date range</td>
            <td>CPU Time, Wait Time, Wall Time and Efficiency of the project on the <strong>researcher funded partitions</strong> within the query’s start and end date.</td>
        </tr>
        <tr>
            <td>6</td>
            <td>Researcher Funded Partitions data to present</td>
            <td>CPU Time, Wait Time, Wall Time and Efficiency of the project on the <strong>researcher funded partitions</strong> from the project start date to present date.</td>
        </tr>
        <tr>
            <td>7</td>
            <td>Core Partitions + Researcher Funded Partitions data in date range</td>
            <td>CPU Time, Wait Time, Wall Time and Efficiency of the project on the <strong>core partitions and researcher funded partitions</strong> within the query’s start and end date.</td>
        </tr>
        <tr>
            <td>8</td>
            <td>Core Partitions + Researcher Funded Partitions data to present</td>
            <td>CPU Time, Wait Time, Wall Time and Efficiency of the project on the <strong>core partitions and researcher funded partitions</strong> from the project start date to present date.</td>
        </tr>
        <tr>
            <td>9</td>
            <td>Total Charge</td>
            <td>Set to N/A.</td>
        </tr>
    </tbody>
</table>



**Project Compute Charts**

---

<table>
    <thead>
        <tr>
            <th><strong>ID</strong></th>
            <th><strong>Title</strong></th>
            <th><strong>Description</strong></th>
        </tr>
    </thead>
    <tbody>
        <tr>
            <td>1</td>
            <td>Rate of usage per month</td>
            <td>Displays the CPU Time, Wait Time and Wall Time per month within the query’s start and end date.</td>
        </tr>
        <tr>
            <td>2</td>
            <td>Cumulative total usage per month</td>
            <td>Displays the cumulative CPU Time, Wait Time and Wall Time per month within the query’s start and end date.</td>
        </tr>
        <tr>
            <td>3</td>
            <td>Top 10 users usage</td>
            <td>Displays the top 10 users of the project by Wall Time within the query’s start and end date.</td>
        </tr>
        <tr>
            <td>4</td>
            <td>Usage by partition</td>
            <td>Displays the usage of partitions within the query’s start and end date.</td>
        </tr>
        <tr>
            <td>5</td>
            <td>Efficiency per month</td>
            <td>Displays the efficiency per month within the query’s start and end date. The table below the chart shows the average efficiency per month within the query’s start and end date as well
                as the project’s start date to the present date.</td>
        </tr>
        <tr>
            <td>6</td>
            <td>Number of jobs per month</td>
            <td>Displays the number of jobs per month within the query's start and end date. The table below the chart shows the total number of jobs within the query’s start and end date as well as
                the project’s start date to the present date.</td>
        </tr>
        <tr>
            <td>7</td>
            <td>Per-Job average stats per month</td>
            <td>Displays the Per-Job average CPU Time, Wait Time and Wall Time per month within the query’s start and end date. The table below the chart shows the Per-Job average CPU Time, Wait Time
                and Wall Time per month within the query’s start and end date as well as the project’s start date to the present date.</td>
        </tr>
        <tr>
            <td>8</td>
            <td>Core count and node utilisation per month</td>
            <td>Displays the core count and node utilisation per month within the query’s start and end date. The table below the chart shows the number of cores and average number of cores per job
                per month within the query’s start and end date as well as the project’s start date to the present date. <strong>Note</strong>: Array jobs in the Compute Daily table display as using a
                single core with multiple jobs.</td>
        </tr>
    </tbody>
</table>



**Filter Projects**

---

Technical leads can filter the compute data analytics by partitions by selecting the ‘Partitions Filter' dropdown option and selecting a partition. 

**Insert images**



**Project Storage Data**

---

**Insert images**

<table>
    <thead>
        <tr>
            <th><strong>ID</strong></th>
            <th><strong>Title</strong></th>
            <th><strong>Description</strong></th>
        </tr>
    </thead>
    <tbody>
        <tr>
            <td>1</td>
            <td>Start date</td>
            <td>Start date of the storage consumption query.</td>
        </tr>
        <tr>
            <td>2</td>
            <td>End date</td>
            <td>End date of the storage consumption query.</td>
        </tr>
        <tr>
            <td>3</td>
            <td>Average disk space usage per week</td>
            <td>Average disk space usage per week for home and scratch.</td>
        </tr>
        <tr>
            <td>4</td>
            <td>Average file count per week</td>
            <td>Average file count per week for home and scratch.</td>
        </tr>
        <tr>
            <td>5</td>
            <td>Disk space per month chart</td>
            <td>Disk space usage per month for home and scratch.</td>
        </tr>
        <tr>
            <td>6</td>
            <td>File count per month chart</td>
            <td>File count per month for home and scratch.</td>
        </tr>
    </tbody>
</table>


**Note**: The start and end date will default to the last twelve months if not defined by the user.



### Data Export

- PDF
- Charts



### Data Import

**Find date range of LIGO file.**

   ```
   python3 manage.py find_date_range_of_ligo_file \
      --file=path_to_ligo_log_file.out
   ```



**Import LIGO daily compute stats.**

   ```
   python3 manage.py import_daily_compute_ligo \
      --file=path_to_stats_file.out
      -d 31 \
      -m 10 \
      -y 2020 \
      -s CF
   ```



**Import daily compute stats.**

   ```
   python3 manage.py import_daily_compute \
      --file=path_to_stats_file.out
      -d 31 \
      -m 10 \
      -y 2020 \
      -s CF
   ```



**Import user last login stats.**

   ```
   python3 manage.py import_user_last_login \
      --file=path_to_user_last_login.csv
   ```



**Import weekly storage stats.**

   ```
   python3 manage.py import_weekly_storage \
      --homefile=path_to_home_file.csv \
      --scratchfile=path_to_scratch_file.csv \
      -d 21 \
      -m 11 \
      -y 2020 \
      -s CF
   ```



### Deployment

#### **Bangor**

---

1. Switch to `arcca` branch.

    ```git checkout arcca```

2. Source environment.

    ```source /path/to/venv```

3. Run database migrations.

    ```python3 manage.py migrate```

4. Load data fixtures.

    ```
    python3 manage.py loaddata \
       access_methods.json \
       applications.json \
       os.json \
       hardware_groups.json \ 
       partitions.json
    ```

5. Migrate PI text field.

    ```
python3 manage.py migrate_pi_text_field
    ```
    
6. Load in historical data.

    - Import daily compute.

        ```
        python3 manage.py import_historical_daily_compute \
           --input_dir=path_to_bz2_files_to_import \
           --output_dir=path_to_move_bz2_files_to_once_processed
        ```

    - Import daily compute ligo.

        ```
        python3 manage.py import_historical_daily_compute_ligo \
           --input_dir=path_to_bz2_files_to_import \
           --output_dir=path_to_move_bz2_files_to_once_processed
        ```

    - Import user last login.

        ```
        python3 manage.py import_historical_user_last_login \
           --input_dir=path_to_csv_files_to_import \
           --output_dir=path_to_move_csv_files_to_once_processed
        ```

    - Import weekly storage.

        ```
        python3 manage.py import_historical_weekly_storage \
           --input_dir=path_to_csv_files_to_import \
           --output_dir=path_to_move_csv_files_to_once_processed
        ```



#### **Cardiff**

---


