from matplotlib import pyplot as plt
import os

from wltp.test import wltp_db_tests as wltpdb


def plot():
    font_size = 8
    tick_size = 6.5

    vehdata = wltpdb._run_the_experiments(transplant_original_gears=False, compare_results=False)
    vehdata['pmr'] = 1000.0 * vehdata['rated_power'] / vehdata['kerb_mass']


    res = wltpdb._vehicles_applicator(wltpdb.gened_fname_glob,
            lambda _, df_g, df_h: (
                df_g['rpm'].mean(), df_g['p_available'].mean(), df_h['n'].mean(), df_h['P_max'].mean())
            )
    res.columns=['gened_mean_rpm', 'gened_mean_p', 'heinz_mean_rpm', 'heinz_mean_p']
    vehdata = vehdata.merge(res, how='inner', left_index=True, right_index=True).sort()

    ax1 = plt.subplot(111)
    ax1.set_xlabel(r'$PMR [\frac{hp}{km/h}]$')

    ax1.set_ylabel(r'$\Delta EnginePower (heinz-gened) [hp]$', color='g')
    for tl in ax1.get_yticklabels():
        tl.set_color('g')

    ax2 = ax1.twinx()
    ax2.set_ylabel(r'$\Delta EngineSpeed (heinz-gened) [rpm]$', color='b')
    for tl in ax2.get_yticklabels():
        tl.set_color('b')


    l_dn = ax1.plot(vehdata.pmr, vehdata.gened_mean_p - vehdata.heinz_mean_p, 'og')
    l_dp = ax2.plot(vehdata.pmr, vehdata.gened_mean_rpm - vehdata.heinz_mean_rpm, '.b')

    plt.title("Difrences of Means with Heinz's 2sec upshift rule")

    ax1.xaxis.grid = True
    ax1.yaxis.grid = True
    ax2.yaxis.grid = True

    plt.show()


if __name__ == '__main__':
    os.chdir(os.path.join(wltpdb.mydir, wltpdb.samples_dir))
    plot()