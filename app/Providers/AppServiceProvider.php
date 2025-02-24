<?php

namespace App\Providers;

use App\Models\User;
use Illuminate\Support\ServiceProvider;
use BezhanSalleh\FilamentLanguageSwitch\LanguageSwitch;
use Illuminate\Database\Eloquent\Model;
use Illuminate\Support\Facades\Route;
use Illuminate\Support\Facades\Gate;

class AppServiceProvider extends ServiceProvider
{
    /**
     * Register any application services.
     */
    public function register(): void
    {
        //
    }

    /**
     * Bootstrap any application services.
     */
    public function boot(): void
    {
        //
        LanguageSwitch::configureUsing(function (LanguageSwitch $switch) {
            $switch
                ->locales(['es','en']); // also accepts a closure
        });

        Model::unguard();

        // Gate::define('viewPulse', function (User $user) {
        //     return true;
        //     // $user->isAdmin();
        // });

        // Route::middleware('api')
        // ->prefix('api')
        // ->group(base_path('routes/api.php'));

        // Route::middleware('web')
        //     ->group(base_path('routes/web.php'));

        }
}
