import pandas as pd
from wayback_search import POLICY_DIR
import os


MASTER_CSV = os.path.join(POLICY_DIR, 'master-privacy-policies-index.csv')


def main():

    policy_indices = [os.path.join(POLICY_DIR, x) for x in os.listdir(POLICY_DIR) if '.csv' in x and 'master' not in x]

    master = None
    first = True
    for index in policy_indices:
        print('processing {}'.format(index))
        df = pd.read_csv(index)
        print(df.columns)
        if first:
            master = df
            first = False
        else:
            master = pd.concat([master, df])


    master.to_csv(MASTER_CSV, index=False)
    print('master csv written to {}'.format(MASTER_CSV))

    return


if __name__ == '__main__':
    main()
