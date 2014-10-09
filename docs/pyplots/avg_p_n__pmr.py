import os

from matplotlib import pyplot as plt
from wltp import model
from wltp.test import wltp_db_tests as wltpdb


def plot(axis, quantity, gened_column, heinz_column):
    font_size = 8
    tick_size = 6.5

    vehdata = wltpdb._run_the_experiments(transplant_original_gears=False, compare_results=False)
    vehdata['pmr'] = 1000.0 * vehdata['rated_power'] / vehdata['kerb_mass']


    res = wltpdb._vehicles_applicator(wltpdb.gened_fname_glob,
            lambda _, df_g, df_h: (
                df_g[gened_column].mean(), df_h[heinz_column].mean())
            )
    res.columns=['gened_mean', 'heinz_mean']
    vehdata = vehdata.merge(res, how='inner', left_index=True, right_index=True).sort()


    axis.set_xlabel(r'$PMR [W/kg]$')

    axis.set_ylabel(r'$%s$' % quantity)
#     for tl in axis.get_yticklabels():
#         tl.set_color('g')

    ax2 = axis.twinx()
    ax2.set_ylabel(r'$\Delta %s$' % quantity, color='r')
    for tl in ax2.get_yticklabels():
        tl.set_color('r')

    ## Plot class-Limits
    #
    class_limits = model.get_class_pmr_limits()
    for limit in class_limits:
        l = plt.axvline(limit, color='y', linewidth=2)
        
    l_gened, = axis.plot(vehdata.pmr, vehdata.gened_mean, 'ob', fillstyle='none')
    l_heinz, = axis.plot(vehdata.pmr, vehdata.heinz_mean, '+g')
    l_dp = ax2.plot(vehdata.pmr, vehdata.gened_mean - vehdata.heinz_mean, '.r')

    plt.legend([l_gened, l_heinz], ['Python', 'Heinz'])
    plt.title("Means of %s compared with Heinz's 2sec upshift rule" % quantity)
    
    axis.xaxis.grid = True
    axis.yaxis.grid = True
    ax2.yaxis.grid = True


if __name__ == '__main__':
    os.chdir(os.path.join(wltpdb.mydir, wltpdb.samples_dir))
    plot(
        axis=plt.subplot(211), 
        quantity='EngineSpeed [rpm]', 
        gened_column='rpm', 
        heinz_column='n'
    )
    plot(
        axis=plt.subplot(212), 
        quantity='EnginePower [kW]', 
        gened_column='p_available', 
        heinz_column='P_max'
    )

    plt.subplots_adjust(hspace=0.4)    
    plt.show()
    
