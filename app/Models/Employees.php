<?php

namespace App\Models;

use Illuminate\Database\Eloquent\Factories\HasFactory;
use Illuminate\Database\Eloquent\Model;
use Illuminate\Database\Eloquent\Relations\HasMany;
use Illuminate\Database\Eloquent\Relations\BelongsTo;

class Employees extends Model
{
    use HasFactory;
    protected $table = 'employeefiles';
    public function branch(): HasMany
    {
        return  $this->hasMany(Branch::class);
    }
    public function jobtitles(): BelongsTo
    {
        return  $this->belongsTo(Jobtitles::class, 'jobtitleid');
    }
    public function timecards()
    {
        return $this->hasManyThrough(Timecards::class, Employees::class, 'id', 'employeeid', 'employeeid', 'id');
    }
    public function employee()
    {
        return $this->belongsTo(Employees::class, 'employeeid');
    }
    protected $appends = ['fullname'];

    public function getFullnameAttribute()
    {
        return "{$this->firstname} {$this->lastname}";
    }
}
